// Create functions at the given RVAs (one hex RVA per line in the file passed as the first argument)
// where Ghidra's auto-analysis didn't define one, typically code reached only through vtables
// or function pointers. Changes the Ghidra database only.
import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;

import java.nio.file.Files;
import java.nio.file.Path;

public class EnsureFunctions extends GhidraScript {
    @Override public void run() throws Exception {
        Address base = currentProgram.getImageBase();
        for (String line : Files.readAllLines(Path.of(getScriptArgs()[0]))) {
            line = line.trim();
            if (line.isEmpty()) continue;
            Address a = base.add(Long.decode(line));
            Function f = getFunctionAt(a);
            if (f != null) { println("ENSURE exists " + line + " " + f.getName()); continue; }
            Function inside = getFunctionContaining(a);
            if (getInstructionAt(a) == null) {
                if (getDataAt(a) != null) clearListing(a);
                new DisassembleCommand(a, null, true).applyTo(currentProgram, monitor);
            }
            f = createFunction(a, null);
            println("ENSURE " + (f != null ? "created " : "FAILED ") + line
                + (inside != null ? " (was inside " + inside.getName() + ")" : "")
                + (f != null ? " size=" + f.getBody().getNumAddresses() : ""));
        }
    }
}
