// Phase 2: export per-function matching evidence as JSON lines.
// Usage (headless): -postScript ExportFunctionFeatures.java <output.jsonl>
// One line per function: rva, size, referenced strings, distinctive scalar constants,
// callee RVAs, caller count, and data-global RVAs it touches. Addresses are RVAs relative to
// the program's image base, so Windows and Mac outputs are comparable in shape.
// Output holds metadata only (strings/constants/addresses), never instruction bytes; keep it outside the repo anyway.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.*;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.scalar.Scalar;
import ghidra.program.model.symbol.Reference;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.util.*;

public class ExportFunctionFeatures extends GhidraScript {
    private Address base;

    private long rva(Address a) { return a.subtract(base); }

    private static String esc(String s) {
        StringBuilder b = new StringBuilder(s.length() + 8);
        for (char c : s.toCharArray()) {
            switch (c) {
                case '"': b.append("\\\""); break;
                case '\\': b.append("\\\\"); break;
                case '\n': b.append("\\n"); break;
                case '\r': b.append("\\r"); break;
                case '\t': b.append("\\t"); break;
                default:
                    if (c < 0x20 || c > 0x7e) b.append(String.format("\\u%04x", (int) c));
                    else b.append(c);
            }
        }
        return b.toString();
    }

    private String stringAt(Address a) {
        Data d = getDataAt(a);
        if (d == null) return null;
        if (d.hasStringValue()) {
            Object v = d.getValue();
            return v == null ? null : v.toString();
        }
        // pointer to a string (common for MSVC/clang string tables)
        if (d.isPointer() && d.getValue() instanceof Address) {
            Data t = getDataAt((Address) d.getValue());
            if (t != null && t.hasStringValue() && t.getValue() != null) return t.getValue().toString();
        }
        return null;
    }

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 1) throw new IllegalArgumentException("need output path");
        base = currentProgram.getImageBase();
        Listing listing = currentProgram.getListing();
        FunctionManager fm = currentProgram.getFunctionManager();
        long count = 0;
        try (BufferedWriter out = new BufferedWriter(new FileWriter(args[0]), 1 << 20)) {
            out.write("{\"meta\":{\"program\":\"" + esc(currentProgram.getName()) + "\",\"image_base\":\"" + base
                    + "\",\"language\":\"" + currentProgram.getLanguageID() + "\",\"compiler\":\""
                    + currentProgram.getCompilerSpec().getCompilerSpecID() + "\"}}\n");
            for (Function f : fm.getFunctions(true)) {
                if (monitor.isCancelled()) break;
                if (f.isExternal()) continue;
                LinkedHashSet<String> strings = new LinkedHashSet<>();
                TreeSet<Long> consts = new TreeSet<>();
                TreeSet<Long> globals = new TreeSet<>();
                TreeSet<Long> disps = new TreeSet<>();
                int insns = 0;
                ArrayList<Long> calls = new ArrayList<>();
                for (Instruction ins : listing.getInstructions(f.getBody(), true)) {
                    insns++;
                    for (Reference r : ins.getReferencesFrom()) {
                        Address to = r.getToAddress();
                        if (r.getReferenceType().isCall() && to.isMemoryAddress() && calls.size() < 256) {
                            Function cf = getFunctionAt(to);
                            if (cf != null && cf.isThunk()) cf = cf.getThunkedFunction(true);
                            if (cf != null && !cf.isExternal()) calls.add(rva(cf.getEntryPoint()));
                            else if (cf != null && cf.getName().startsWith("EXT_FUN_")) {
                                // body lives in a dropped (protected) block; keep its original RVA in order
                                calls.add(Long.parseLong(cf.getName().substring(8), 16) - base.getOffset());
                            }
                            continue;
                        }
                        if (!to.isMemoryAddress() || r.getReferenceType().isFlow()) continue;
                        String s = stringAt(to);
                        if (s != null) { if (s.length() >= 4 && strings.size() < 64) strings.add(s); continue; }
                        MemoryBlock blk = getMemoryBlock(to);
                        if (blk != null && !blk.isExecute() && globals.size() < 128) globals.add(rva(to));
                    }
                    for (int op = 0; op < ins.getNumOperands(); op++) {
                        Object[] objs = ins.getOpObjects(op);
                        boolean hasReg = false, stackReg = false;
                        for (Object o : objs) if (o instanceof ghidra.program.model.lang.Register) {
                            hasReg = true;
                            String rn = ((ghidra.program.model.lang.Register) o).getName().toUpperCase();
                            if (rn.equals("RSP") || rn.equals("RBP") || rn.equals("ESP") || rn.equals("EBP")) stackReg = true;
                        }
                        // struct-member displacements: [reg+disp] off a non-stack base register
                        if (hasReg && !stackReg && ins.getOperandType(op) != 0
                                && (ins.getOperandType(op) & ghidra.program.model.lang.OperandType.DYNAMIC) != 0) {
                            for (Object o : objs) if (o instanceof Scalar) {
                                long v = ((Scalar) o).getSignedValue();
                                if (v >= 8 && v < 0x40000 && disps.size() < 256) disps.add(v);
                            }
                        }
                        for (Object o : objs) {
                            if (!(o instanceof Scalar)) continue;
                            long v = ((Scalar) o).getUnsignedValue();
                            // keep distinctive values: big enough to be rare, not obviously an address.
                            // A scalar next to a register is a displacement ([reg+disp]) even when it
                            // happens to fall inside the image (Mac image base is 0).
                            if (v >= 0x1000 && v != 0xffffffffL && v != 0xffffffffffffffffL
                                    && (hasReg || getMemoryBlock(toAddr(v)) == null) && consts.size() < 96) consts.add(v);
                        }
                    }
                }
                TreeSet<Long> callees = new TreeSet<>();
                for (Function c : f.getCalledFunctions(monitor)) {
                    Function t = c.isThunk() ? c.getThunkedFunction(true) : c;
                    if (t != null && !t.isExternal()) callees.add(rva(t.getEntryPoint()));
                    else if (t != null) strings.add("@import:" + t.getName());
                }
                int callers = f.getCallingFunctions(monitor).size();
                StringBuilder b = new StringBuilder(256);
                b.append("{\"rva\":").append(rva(f.getEntryPoint()))
                        .append(",\"size\":").append(f.getBody().getNumAddresses())
                        .append(",\"insns\":").append(insns)
                        .append(",\"name\":\"").append(esc(f.getName())).append('"')
                        .append(",\"callers\":").append(callers)
                        .append(",\"thunk\":").append(f.isThunk())
                        .append(",\"strings\":[");
                boolean first = true;
                for (String s : strings) { if (!first) b.append(','); first = false; b.append('"').append(esc(s)).append('"'); }
                b.append("],\"consts\":").append(consts.toString().replace(" ", ""))
                        .append(",\"callees\":").append(callees.toString().replace(" ", ""))
                        .append(",\"globals\":").append(globals.toString().replace(" ", ""))
                        .append(",\"calls\":").append(calls.toString().replace(" ", ""))
                        .append(",\"disps\":").append(disps.toString().replace(" ", ""))
                        .append("}\n");
                out.write(b.toString());
                if (++count % 10000 == 0) println("exported " + count);
            }
        }
        println("FEATURES done functions=" + count + " -> " + args[0]);
    }
}
