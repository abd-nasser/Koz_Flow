from rest_framework import serializers
from .models import kozUser

# ----- SERIALIZER POUR L'INSCRIPTION -----
class RegisterSerializers(serializers.ModelSerializer):
    
    password = serializers.CharField(
        write_only =True,
        required=True,
         style={'input_type':'password'}
         )
    
    password2= serializers.CharField(
        write_only =True,
        required=True,
         style={'input_type':'password'}
         )
    class Meta:
        model = kozUser
        fields = ["email", "nom_complet", "telephone", 'adresse', "password", "password2", "role"]
        
        
        #verifie la compatibilté des mots de passe fournis par user
    def validate(self, attrs):
            if attrs["password"] != attrs["password2"]:
                raise serializers.ValidationError({"password":"Les mots de passe ne correspondent pas"})
            return attrs
        
        #creations du user apres verification des mot de passe
    def create(self, validated_data):
        validated_data.pop("password2")
        password = validated_data.pop("password")

        user = kozUser.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user
         

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = kozUser
        fields =  ['id', 'email', 'nom_complet', 'telephone', 'adresse', 'role', 'is_staff', 'is_active',]
            
    