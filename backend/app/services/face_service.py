import torch
from facenet_pytorch import MTCNN, InceptionResnetV1
from PIL import Image
import numpy as np

class FaceRecognitionService:
    def __init__(self):
        # Deteksi otomatis device (GPU/MPS/CPU)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Menginisialisasi Model AI pada perangkat: {self.device}")
        
        # 1. MTCNN (Multi-task Cascaded Convolutional Networks)
        # Digunakan untuk mendeteksi wajah dan memotongnya (Face Cropping & Alignment)
        self.mtcnn = MTCNN(
            image_size=160, margin=0, min_face_size=20,
            thresholds=[0.6, 0.7, 0.7], factor=0.709, post_process=True,
            device=self.device
        )
        
        # 2. FaceNet (InceptionResnetV1 pre-trained pada dataset VGGFace2)
        # Digunakan untuk mengekstrak wajah yang sudah dipotong menjadi vektor 512 dimensi.
        self.resnet = InceptionResnetV1(pretrained='vggface2').eval().to(self.device)

    def extract_embedding(self, image: Image.Image) -> list[float]:
        """
        Menerima objek PIL Image mentah dari kamera.
        Mengembalikan list Python berisi 512 angka float (Face Embedding).
        Jika tidak ada wajah terdeteksi, mengembalikan None.
        """
        # Pastikan gambar dalam mode RGB
        if image.mode != 'RGB':
            image = image.convert('RGB')
            
        # MTCNN mendeteksi wajah dan mengembalikan tensor gambar wajah yang sudah distandarisasi (160x160)
        face_tensor = self.mtcnn(image)
        
        if face_tensor is None:
            return None # Wajah tidak ditemukan
            
        # Tambahkan dimensi batch (karena resnet mengharapkan tensor berdimensi [batch, channels, height, width])
        face_tensor = face_tensor.unsqueeze(0).to(self.device)
        
        # Nonaktifkan gradien karena kita hanya melakukan inferensi, bukan training (Zero-Retraining Pipeline)
        with torch.no_grad():
            embedding_tensor = self.resnet(face_tensor)
            
        # Konversi tensor (GPU/CPU) kembali menjadi array numpy 1D, lalu ke list Python murni untuk disimpan di database
        embedding_list = embedding_tensor.cpu().numpy().flatten().tolist()
        return embedding_list
        
    def aggregate_embeddings(self, embeddings: list[list[float]]) -> list[float]:
        """
        Menghitung nilai rata-rata (Agregat) dari beberapa vektor.
        Digunakan saat proses Enrollment untuk meningkatkan ketahanan (robustness) terhadap berbagai angle.
        """
        if not embeddings:
            return None
        # Ubah ke array numpy untuk kalkulasi matriks yang efisien
        np_embeddings = np.array(embeddings)
        # Hitung mean di sepanjang sumbu 0 (rata-rata per kolom dimensi)
        avg_embedding = np.mean(np_embeddings, axis=0)
        # Normalisasi vektor (L2 Norm) agar magnitude vektor menjadi 1, ini krusial untuk Cosine Similarity
        norm_embedding = avg_embedding / np.linalg.norm(avg_embedding)
        return norm_embedding.tolist()

    def detect_face(self, image: Image.Image) -> dict:
        """
        Mendeteksi wajah dan mengembalikan koordinat kotak (bbox) dan landmarks.
        """
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        boxes, probs, landmarks = self.mtcnn.detect(image, landmarks=True)
        
        if boxes is None or len(boxes) == 0:
            return None
            
        # Ambil wajah terbesar
        box_areas = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])
        idx = np.argmax(box_areas)
        
        return {
            "box": boxes[idx].tolist(), # [x1, y1, x2, y2]
            "prob": float(probs[idx]),
            "landmarks": landmarks[idx].tolist()
        }

    def validate_face_pose(self, image: Image.Image, expected_pose: str) -> dict:
        """
        Memvalidasi apakah wajah menghadap ke arah yang benar (Yaw/Pitch) menggunakan Facial Landmarks.
        expected_pose: 'depan', 'kanan', 'kiri', 'bawah'
        """
        if image.mode != 'RGB':
            image = image.convert('RGB')
            
        # MTCNN bisa mengembalikan kotak wajah dan titik landmark
        boxes, probs, landmarks = self.mtcnn.detect(image, landmarks=True)
        
        if boxes is None or landmarks is None or len(boxes) == 0:
            return {"valid": False, "message": "Wajah tidak terdeteksi. Posisikan wajah di tengah layar."}

        # Ambil wajah yang ukurannya paling besar (mencegah deteksi wajah orang di belakang)
        box_areas = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])
        largest_idx = np.argmax(box_areas)
        landmark = landmarks[largest_idx]

        # Landmark MTCNN: index 0 (mata kiri), 1 (mata kanan), 2 (hidung), 3 (mulut kiri), 4 (mulut kanan)
        left_eye, right_eye, nose, left_mouth, right_mouth = landmark

        # Kalkulasi Yaw (Rotasi Kiri/Kanan): Membandingkan jarak hidung ke mata kiri vs mata kanan
        dist_left_eye_nose = np.linalg.norm(left_eye - nose)
        dist_right_eye_nose = np.linalg.norm(right_eye - nose)
        
        # Rasio > 1.2 biasanya nengok kanan. Rasio < 0.8 biasanya nengok kiri.
        yaw_ratio = dist_left_eye_nose / (dist_right_eye_nose + 1e-6)

        # Kalkulasi Pitch (Mendongak/Menunduk): Membandingkan jarak hidung-mata vs hidung-mulut
        dist_eyes_nose = (dist_left_eye_nose + dist_right_eye_nose) / 2
        dist_mouth_nose = (np.linalg.norm(left_mouth - nose) + np.linalg.norm(right_mouth - nose)) / 2
        
        # Rasio > 1.1 biasanya menunduk (hidung lebih dekat ke mulut)
        pitch_ratio = dist_eyes_nose / (dist_mouth_nose + 1e-6)

        if expected_pose == "depan":
            if 0.7 < yaw_ratio < 1.3 and 0.7 < pitch_ratio < 1.3:
                return {"valid": True, "message": "Sempurna! Tahan posisi Anda..."}
            return {"valid": False, "message": "Tatap lurus ke depan, sejajarkan wajah."}
            
        elif expected_pose == "kanan":
            if yaw_ratio > 1.25: # Direlaksasi dari 1.4 (tidak perlu nengok terlalu tajam)
                return {"valid": True, "message": "Bagus! Menangkap bingkai kanan..."}
            return {"valid": False, "message": "Kurang menoleh. Tolehkan kepala Anda ke KANAN."}
            
        elif expected_pose == "kiri":
            if yaw_ratio < 0.8: # Direlaksasi dari 0.7
                return {"valid": True, "message": "Bagus! Menangkap bingkai kiri..."}
            return {"valid": False, "message": "Kurang menoleh. Tolehkan kepala Anda ke KIRI."}
            
        elif expected_pose == "bawah":
            if pitch_ratio > 1.15: # Direlaksasi dari 1.2
                return {"valid": True, "message": "Bagus! Menangkap bingkai bawah..."}
            return {"valid": False, "message": "Kurang menunduk. Tundukkan kepala Anda."}

        return {"valid": False, "message": "Menyesuaikan posisi..."}

# Inisialisasi instance global agar model AI tetap berada di memori RAM dan tidak di-load ulang setiap kali ada request
face_service = FaceRecognitionService()
