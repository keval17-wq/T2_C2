import java.net.InetAddress;

public class ClientInfo {
    InetAddress addr;
    int port;

    public ClientInfo(InetAddress a, int b){
        addr = a;
        port = b;
    }

    public InetAddress getAddress(){
        return addr;
    }

    public int getPort(){
        return port;
    }

    public void updateAddress(InetAddress a){
        addr = a;
    }

    public void updatePort(int p){
        port = p;
    }
}
