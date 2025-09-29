# seguridad/services/rekog.py
import boto3, io
from django.conf import settings
REKOG_REGION = "us-east-1"                 # ajusta
REKOG_COLLECTION = settings.AWS_REKOGNITION_COLLECTION_ID

rekog = boto3.client("rekognition", region_name=REKOG_REGION)

def search_known_face(image_bytes: bytes, threshold=90.0, max_faces=1):
    """Busca rostros registrados en la colección."""
    resp = rekog.search_faces_by_image(
        CollectionId=REKOG_COLLECTION,
        Image={"Bytes": image_bytes},
        FaceMatchThreshold=threshold,
        MaxFaces=max_faces,
    )
    matches = resp.get("FaceMatches", [])
    return matches  # lista (puede venir vacía)

def detect_faces(image_bytes: bytes):
    """Solo detección (sin identificar)."""
    return rekog.detect_faces(Image={"Bytes": image_bytes}, Attributes=["DEFAULT"])


# Al final de seguridad/services/rekog.py

def detect_text(jpg_bytes):
    """
    Detecta texto en una imagen usando AWS Rekognition.
    """
    resp = rekog.detect_text(
        Image={'Bytes': jpg_bytes}
    )
    return resp.get("TextDetections", [])