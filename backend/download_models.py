from facenet_pytorch import MTCNN, InceptionResnetV1
import torch

def download():
    print("Downloading MTCNN models...")
    MTCNN(device='cpu')
    print("Downloading FaceNet (vggface2) models...")
    InceptionResnetV1(pretrained='vggface2').eval()
    print("Done!")

if __name__ == "__main__":
    download()
