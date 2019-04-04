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
  server = new Server(this, port);
  println("server address: " + server.ip());
  
  sound = new SoundFile(this, "gong.mp3");
  
  size(480, 320);
  camera = new Capture(this, width, height, 12);
  camera.start();
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
