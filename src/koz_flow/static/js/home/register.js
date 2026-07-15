document.addEventListener('DOMContentLoaded', function(){
    const registerForm = document.getElementById('registerForm');
    const registerFormError = document.getElementById('registerError');
    const registerBtn = document.getElementById('registerBtn');

    if (registerForm){
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            // 1️⃣ Récupérer les données du formulaire
            const email = document.getElementById("reg_email").value.trim();
            const nom_complet = document.getElementById("reg_nom").value.trim();
            const telephone = document.getElementById('reg_telephone').value.trim();
            const pays = document.getElementById("reg_pays").value.trim();
            const ville =  document.getElementById("reg_ville").value.trim();
            const adresse = document.getElementById("reg_adresse").value.trim();
            const genre = document.getElementById("reg_genre").value;
            const profession = document.getElementById('reg_profession').value;
            const password = document.getElementById("reg_password").value;
            const password2 = document.getElementById('reg_password2').value;

            // 2️⃣ Validation de base
            if (!email || !nom_complet || !telephone || !password || !password2 || !pays || !ville){
                showRegisterError('Tous les champs obligatoires doivent être remplis.');
                return;
            }

            if (password !== password2){
                showRegisterError('Les mots de passe ne correspondent pas.');
                return;
            }

            if (password.length < 6 ){  // ← CORRIGÉ : length au lieu de lenght
                showRegisterError('Le mot de passe doit contenir au moins 6 caractères.');
                return;
            }

            // 3️⃣ Construire le body pour l'API
            const body = {
                email: email,
                nom_complet: nom_complet,
                telephone: telephone,
                adresse: adresse,
                pays: pays,
                ville: ville,
                genre: genre,
                profession: profession,
                password: password,
                password2: password2
            };
            console.log("🔵 Body envoyé:", body);

            // 4️⃣ Désactiver le bouton
            registerBtn.disabled = true;
            registerBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> En cours...';
            registerFormError.classList.add("hidden");

            try{
                // 5️⃣ Envoyer la requête à l'API (URL dynamique)
                const apiBase = window.location.origin;
                const response = await fetch("http://127.0.0.1:8000/api/auth/register/", {
                    method: "POST",
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    credentials: 'include',
                    body: JSON.stringify(body)
                });

                const data = await response.json();
                console.log('🔵 Réponse API:', data);

                // 6️⃣ Traiter la réponse
                if (response.ok) {
                    // ✅ Inscription réussie
                    alert("✅ Compte créé avec succès ! Connexion automatique en cours...");
                    document.getElementById("register_modal").close();  // ← CORRIGÉ : close()

                    // 🔥 Connexion automatique après inscription
                    try {
                        const loginResponse = await fetch("http://127.0.0.1:8000/api/auth/login/", {
                            lmethod: 'POST',
                            headers: {
                                
                                'Content-Type': 'application/json',
                                'Authorization': 'Bearer ' + localStorage.getItem('access'),
                                'X-CSRFToken': getCookie('csrftoken') || ''
                            },
                            credentials: 'include',
                            body: JSON.stringify({ email, password })
                        });

                        const loginData = await loginResponse.json();

                        if (loginResponse.ok){
                            console.log('🔵 Connexion automatique réussie !');
                            localStorage.setItem('access', loginData.access);
                            localStorage.setItem('refresh', loginData.refresh);
                            localStorage.setItem('user', JSON.stringify(loginData.user));
                            
                            // ✅ Redirection selon le rôle
                            if (loginData.redirect_url) {
                                window.location.href = loginData.redirect_url;
                            } else {
                                window.location.href = '/';
                            }
                        } else {
                            console.warn('⚠️ Connexion automatique échouée, redirection vers login.');
                            window.location.href = '/';
                        }
                    } catch (loginError) {
                        console.error('❌ Erreur lors de la connexion automatique:', loginError);
                        window.location.href = '/';
                    }

                } else {
                    // ❌ Erreur API
                    const errorMsg = data.error || data.errors || "Erreur lors de l'inscription.";
                    if (typeof errorMsg === 'object') {
                        const firstError = Object.values(errorMsg)[0];
                        showRegisterError(Array.isArray(firstError) ? firstError[0] : firstError);
                    } else {
                        showRegisterError(errorMsg);
                    }
                }
            } catch (error) {
                console.error('❌ Erreur réseau:', error);
                showRegisterError('Erreur de connexion au serveur. Veuillez réessayer.');
            } finally {
                // 7️⃣ Réactiver le bouton
                registerBtn.disabled = false;
                registerBtn.innerHTML = '<i class="fas fa-user-plus"></i> S\'inscrire';
            }
        });
    }

    // Fonction d'affichage d'erreur
    function showRegisterError(message){
        const registerFormError = document.getElementById('registerError');
        if (registerFormError) {
            registerFormError.textContent = message;
            registerFormError.classList.remove('hidden');
        }
    }

    // Fonction pour récupérer le cookie CSRF
    function getCookie(name){
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + "=")){  // ← CORRIGÉ : length
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;  // ← CORRIGÉ : déplacé à l'intérieur
    }
});