// Prints basic stats so we can confirm a saved Ghidra program opens intact.
import ghidra.app.script.GhidraScript;
public class ProgramStats extends GhidraScript {
    @Override public void run() throws Exception {
        println("STATS program=" + currentProgram.getName()
            + " functions=" + currentProgram.getFunctionManager().getFunctionCount()
            + " symbols=" + currentProgram.getSymbolTable().getNumSymbols()
            + " analyzed=" + currentProgram.getOptions("Program Information").getBoolean("Analyzed", false));
    }
}
