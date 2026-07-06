from rest_framework import serializers
from .models import kozUser

class RegisterSerializers(serializers.ModelSerializer):
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = kozUser
        fields = [
            "email", 
            "nom_complet", 
            "telephone", 
            "adresse",
            "pays",
            "ville",
            "profession",
            "password", 
            "password2"
        ]
        
        # ✅ Sécurité : le role est défini par défaut, pas par l'utilisateur
        # ✅ L'ID est auto-généré, pas besoin de le demander
    
    def validate(self, attrs):
        """Vérifie que les mots de passe correspondent"""
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({
                "password": "Les mots de passe ne correspondent pas"
            })
        return attrs
    
    def create(self, validated_data):
        """Crée l'utilisateur avec les données validées"""
        # ✅ Supprimer password2 (champ virtuel)
        validated_data.pop("password2")
        
        # ✅ Récupérer le password pour le hasher
        password = validated_data.pop("password")
        
        # ✅ Créer l'utilisateur avec le gestionnaire personnalisé
        user = kozUser.objects.create_user(
            email=validated_data.get("email"),
            nom_complet=validated_data.get("nom_complet"),
            telephone=validated_data.get("telephone"),
            password=password,  # ← Le gestionnaire va hasher
            adresse=validated_data.get("adresse", ""),  # ← Optionnel
            pays=validated_data.get("pays", ""),  # ← Optionnel
            ville=validated_data.get("ville", ""),  # ← Optionnel
            profession=validated_data.get("profession", ""),  # ← Optionnel
        )
        
        # ✅ Le rôle est déjà "client" par défaut dans le modèle
        # Pas besoin de le définir ici
        
        return user


class UserSerializer(serializers.ModelSerializer):
    """Serializer pour afficher les infos d'un utilisateur"""
    class Meta:
        model = kozUser
        fields = [
            'id', 
            'email', 
            'nom_complet', 
            'telephone', 
            'adresse', 
            'pays',
            'ville',
            'profession',
            'role', 
            'is_staff', 
            'is_active',
            'date_inscription',
            'est_en_ligne',  # ✅ Ajout du statut en ligne
        ]
            
    