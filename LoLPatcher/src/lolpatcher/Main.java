package lolpatcher;


import java.awt.Point;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.io.StringWriter;
import java.util.ArrayList;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;
import nl.xupwup.Util.GLFramework;
import nl.xupwup.WindowManager.Window;
import nl.xupwup.WindowManager.Components.TextField;

/**
 *
 * @author Rick Hendricksen
 */
public class Main extends Thread {
    public static int patcherVersion;
    static{
        try(BufferedReader br = new BufferedReader(new InputStreamReader(GLFramework.class.getResourceAsStream("/version")))){
            patcherVersion = Integer.parseInt(br.readLine());
        }catch (IOException ex) {
            patcherVersion = Integer.MAX_VALUE;
            Logger.getLogger(Main.class.getName()).log(Level.SEVERE, null, ex);
        }
        System.out.println("Patcher version is " + patcherVersion);
    }
    public List<PatchTask> patchers;
    int currentPatcher = -1;
    PatchTask patcher;

    Flow flow;
    public String airversion;
    long patcherStartTime;
    boolean ignoreS_OK = false, force = false;
    boolean purgeAfterwards = false;
    boolean changeRegionSettings = false;
    float playw, playh, playx, playy, repairw;
    boolean autostart;
    
    public Main(){
        patchers = new ArrayList<>();
    }
    
    public void rerun(){
        patchers.clear();
        if(currentPatcher == -1){
            patchers.add(new SelfUpdateTask());
        }
        
        patchers.add(new ConfigurationTask(this));
        patcher = null;
        currentPatcher = -1;
    }


    private boolean updatePatcher(){
        if(patcher == null || patcher.done){
            if(patcher != null){
                try {
                    patcher.join();
                } catch (InterruptedException ex) {
                    Logger.getLogger(Main.class.getName()).log(Level.SEVERE, null, ex);
                }
            }
            if(currentPatcher == patchers.size()-1){
                return true;
            }
            currentPatcher++;
            patcher = patchers.get(currentPatcher);
            patcher.start();
            patcherStartTime = System.currentTimeMillis();
        }
        
        return false;
    }
    


    public void draw() {
        if(patcher != null){
            if(patcher.error != null){
                try {
                    java.io.File log = new java.io.File("PATCHLOG.txt");
                    log.createNewFile();
                    try(PrintWriter pw = new PrintWriter(log)){
                        patcher.error.printStackTrace(pw);
                    }
                } catch (IOException ex) {
                    Logger.getLogger(Main.class.getName()).log(Level.SEVERE, null, ex);
                }
                StringWriter sw = new StringWriter();
                try(PrintWriter pw = new PrintWriter(sw)){
                    patcher.error.printStackTrace(pw);
                }
                patcher.error = null;
                Window win = new Window(new Point(0, 200), "Error");
                win.addComponent(new TextField(1000, 200, sw.toString().replaceAll("[\r\t]", ""), null));
            }
            PatchTask lp = patcher;          
           
            if(lp instanceof LoLPatcher){
                LoLPatcher ptch = (LoLPatcher) lp;
                if(ptch.workers != null){
                    ArrayList<Worker> workers = new ArrayList<>(ptch.workers.length);
                    for(Worker worker : ptch.workers){
                        if(worker.startTime != -1){
                            workers.add(worker);
                        }
                    }
                }
            }
        }

        if(updatePatcher()){
            System.out.println("Download is done!");
            System.exit(0);
        }
    }

    public void run() {
    	rerun();
        mainLoop();
    }
    
    private void mainLoop() {
        while (true) {
            draw();
        }
    }
    
    
    public static void main(String[] args){
        try{
        	new Main().run();
        }catch(Exception e){
            e.printStackTrace();
            try {
                java.io.File log = new java.io.File("GUILOG.txt");
                log.createNewFile();
                try(PrintWriter pw = new PrintWriter(log)){
                    e.printStackTrace(pw);
                }
            } catch (IOException ex) {
                Logger.getLogger(Main.class.getName()).log(Level.SEVERE, null, ex);
            }
            
        }
    }
}