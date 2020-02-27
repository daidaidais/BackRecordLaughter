import processing.net.*;
import processing.video.*;
import java.util.Date;
import java.io.File;
import processing.sound.*;
SoundFile sound;
Capture camera;

int port = 10001;

Server server;

void setup() {
  size(480, 270);
  
  server = new Server(this, port);
  println("server address: " + server.ip());
  
  sound = new SoundFile(this, "gong.mp3");
  println("Sound is loaded");
  
  String jpgPath = sketchPath();
  println("Listing all filenames in a directory: ");
  String[] filenames = listFileNames(jpgPath+"/data");
  printArray(filenames);
  for(int i=0;i<filenames.length;i++){
    boolean isJpg = filenames[i].contains("jpg");
    if(isJpg){
     File deleteJpg = new File(dataPath(filenames[i]));
     deleteJpg.delete();
    }
  }
  
  String[] cameras = Capture.list();
  
  if (cameras.length == 0) {
    println("There are no cameras available for capture.");
    exit();
  } else {
    println("Available cameras:");
    for (int i = 0; i < cameras.length; i++) {
      println(cameras[i]);
    }
    
    // The camera can be initialized directly using an 
    // element from the array returned by list():
    camera = new Capture(this, width, height, cameras[0]);
    camera.start();     
  }
}

void draw() {
  
  //if UDP is sent from Laugh Detector, play gong
  Client client = server.available();
  if (client !=null) {
    String whatClientSaid = client.readString();
    if (whatClientSaid != null) {
      println(whatClientSaid);
      sound.play();
    } 
  }
  image(camera, 0, 0);
  
  Date d = new Date();
  //println(d.getTime());
  long thresh_time = (d.getTime() / 100) - 300; //delete files older than 30 secs
  File delete_f = new File(dataPath(thresh_time+".jpg"));
  if(delete_f.exists()){
   delete_f.delete();
   //println(thresh_time+".jpg deleted");
  }
  
  saveFrame("data/"+(d.getTime() / 100)+".jpg"); 
}

void captureEvent(Capture camera) {
  camera.read();
}

// This function returns all the files in a directory as an array of Strings  
String[] listFileNames(String dir) {
  File file = new File(dir);
  if (file.isDirectory()) {
    String names[] = file.list();
    return names;
  } else {
    // If it's not a directory
    return null;
  }
}
