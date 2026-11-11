// Decompile the functions containing the given RVAs into one text file per function.
// Args: <rva list file (one hex RVA per line)> <output directory>
// Output is for local side-by-side comparison only ($FM27_WORK_DIR/decomp/), never committed.
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;

import java.io.FileWriter;
import java.nio.file.Files;
import java.nio.file.Path;

public class DecompileFunctions extends GhidraScript {
    @Override public void run() throws Exception {
        String[] args = getScriptArgs();
        Address base = currentProgram.getImageBase();
        Path out = Path.of(args[1]);
        Files.createDirectories(out);
        DecompInterface di = new DecompInterface();
        di.openProgram(currentProgram);
        for (String line : Files.readAllLines(Path.of(args[0]))) {
            line = line.trim();
            if (line.isEmpty() || line.startsWith("#")) continue;
            Address a = base.add(Long.decode(line));
            Function f = getFunctionContaining(a);
            if (f == null) { println("DECOMP none " + line); continue; }
            long frva = f.getEntryPoint().subtract(base);
            DecompileResults r = di.decompileFunction(f, 120, monitor);
            String text = r.decompileCompleted() ? r.getDecompiledFunction().getC() : ("// failed: " + r.getErrorMessage());
            Path file = out.resolve(String.format("%s_%x.c", currentProgram.getName(), frva));
            try (FileWriter w = new FileWriter(file.toFile())) {
                w.write(String.format("// %s function 0x%x (requested 0x%x) image_base %s%n", currentProgram.getName(), frva, a.subtract(base), base));
                w.write(text);
            }
            println("DECOMP " + line + " -> " + file.getFileName());
        }
        di.dispose();
    }
}
