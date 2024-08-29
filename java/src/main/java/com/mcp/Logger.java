package main.java.com.mcp;

public class Logger {

    public static void log(String message) {
        System.out.println("[LOG] " + message);
    }

    public static void logError(String error) {
        System.err.println("[ERROR] " + error);
    }
}
