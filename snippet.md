
nasserdevtes@gmail.com : PNnMqFU650

<div class="scroll-area">
    <div class="content-block">🚗 BIENVENUE CHEZ KOZ SERVICES</div>
    <div class="content-block">💳 CRÉDIT SANS BANQUE</div>
    <div class="content-block">🌍 DIASPORA, COMMANDEZ ICI</div>
    
    <div  class="content-block  ">
        <a href="#">📞 Catalogue</a></div>
</div>

<div class="frame-container">
    <img id="frame" src="{% static 'frames/frame-0001.jpg' %}" alt="">
</div>

<script>
    gsap.registerPlugin(ScrollTrigger);

    // REMPLACE PAR LE NOMBRE EXACT D'IMAGES
    const totalFrames = 120; // ← À MODIFIER !
    const basePath = "{% static 'frames/frame-' %}";
    const frameImg = document.getElementById('frame');

    ScrollTrigger.create({
        trigger: "body",
        start: "top top",
        end: "bottom bottom",
        scrub: 0.8,
        onUpdate: (self) => {
            let frameIndex = Math.floor(self.progress * (totalFrames - 1)) + 1;
            frameIndex = Math.min(frameIndex, totalFrames);
            const paddedIndex = String(frameIndex).padStart(4, '0');
            frameImg.src = `${basePath}${paddedIndex}.jpg`;
        }
    });
</script>


<!-- templates/includes/navbar.html -->
<nav class="navbar bg-base-100 shadow-md fixed top-0 z-50 w-full border-b border-gray-200/20 backdrop-blur-sm bg-white/80">
    <div class="container mx-auto px-4 flex justify-between items-center">
        
        <!-- Logo -->
        <div class="flex items-center gap-2">
            <div class="w-15 h-15 bg-gradient-to-br from-white to-blue-600 rounded-xl flex items-center justify-center shadow-md">
                <img src="{% static 'images/koz_logo_noBack.png' %}" alt="Logo" class="text-white font-bold text-xl">
            </div>
            <span class="text-xl font-bold text-gray-800 hidden sm:inline">KOZ Services</span>
        </div>

        <!-- Liens (centraux) -->
        <div class="hidden md:flex gap-6 text-gray-600 font-medium">
            <a href="#" class="hover:text-blue-600 transition">Accueil</a>
            <a href="#" class="hover:text-blue-600 transition">Catalogue</a>
            <a href="#" class="hover:text-blue-600 transition">Financement</a>
            <a href="#" class="hover:text-blue-600 transition">A propos</a>
            <a href="#" class="hover:text-blue-600 transition">Contact</a>
        </div>

        <!-- Boutons droite -->
        <div class="flex items-center gap-3">
            {% if user.is_authenticated %}
                <a href="{% url 'client_app:client-view' %}" class="hidden sm:inline-block text-sm text-gray-600 hover:text-blue-600 transition">
                    <i class="fas fa-user mr-1"></i> Espace client
                </a>
                <button id="logoutBtn" class="btn btn-error btn-sm text-white">
                    <i class="fas fa-sign-out-alt"></i> Déconnexion
                </button>
            {% else %}
                <button onclick="document.getElementById('login_modal').showModal()" 
                        class="btn btn-ghost btn-sm hidden sm:inline-block">
                    Connexion
                </button>
                <button onclick="document.getElementById('register_modal').showModal()" 
                        class="btn bg-blue-600 btn-sm text-white">
                    <i class="fas fa-user-plus"></i> Inscription
                </button>
            {% endif %}
        </div>

        <!-- Menu burger (mobile) -->
        <div class="md:hidden">
            <button id="burgerBtn" class="btn btn-ghost btn-sm">
                <i class="fas fa-bars text-xl"></i>
            </button>
        </div>
    </div>

    <!-- Menu mobile (caché par défaut) -->
    <div id="mobileMenu" class="hidden md:hidden bg-white border-t border-gray-200 p-4">
        <div class="flex flex-col gap-3 text-gray-600">
            <a href="#" class="hover:text-blue-600">Accueil</a>
            <a href="#" class="hover:text-blue-600">Catalogue</a>
            <a href="#" class="hover:text-blue-600">Financement</a>
            <a href="#" class="hover:text-blue-600">A propos</a>
            <a href="#" class="hover:text-blue-600">Contact</a>
        </div>
    </div>
</nav>

<script>
    document.getElementById('burgerBtn')?.addEventListener('click', function() {
        const menu = document.getElementById('mobileMenu');
        menu.classList.toggle('hidden');
    });
</script>



<div class="absolute top-10 left-10 w-72 h-72 bg-white rounded-full blur-3xl"></div>
        <div class="absolute bottom-10 right-10 w-96 h-96 bg-blue-400 rounded-full blur-3xl"></div>
    

    {% load static %}
{% load tailwind_tags %}
{% load humanize %}
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
    {% tailwind_css %}
    <title>KOZ Services - Votre voiture à crédit, vos pièces en ligne</title>
    <link rel="stylesheet" href="{% static 'css/home/home_style.css' %}">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
</head>
<body>

<!-- ========== NAVBAR ========== -->
<nav class="navbar bg-white/80 backdrop-blur-md shadow-sm fixed top-0 z-50 w-full border-b border-gray-200/40">
    <div class="container mx-auto px-4 flex justify-between items-center h-16">
        
        <!-- Logo -->
        <div class="flex items-center gap-3">
            <a href="{% url 'home_app:home-page' %}" class="flex items-center gap-2">
                <div class="w-10 h-10 bg-gradient-to-br from-blue-600 to-blue-800 rounded-xl flex items-center justify-center shadow-md">
                    <img src="{% static 'images/koz_logo_noBack.png' %}" alt="KOZ" class="w-8 h-8 object-contain">
                </div>
                <span class="text-xl font-bold text-gray-800 hidden sm:inline">KOZ Services</span>
            </a>
        </div>

        <!-- Liens centraux -->
        <div class="hidden md:flex gap-6 text-gray-600 font-medium text-sm">
            <a href="{% url 'home_app:home-page' %}" class="hover:text-blue-600 transition">Accueil</a>
            <a href="{% url 'vehicul_app:list-vehicul' %}" class="hover:text-blue-600 transition">Catalogue</a>
            <a href="#" class="hover:text-blue-600 transition">Financement</a>
            <a href="#" class="hover:text-blue-600 transition">Contact</a>
        </div>

        <!-- Actions -->
        <div class="flex items-center gap-4">
            {% if user.is_authenticated %}
                <a href="{% url 'client_app:client-view' %}" class="hidden sm:flex items-center gap-2 text-sm text-gray-700 hover:text-blue-600 transition font-medium">
                    <i class="fas fa-user-circle text-lg text-blue-600"></i>
                    {{ user.nom_complet }}
                </a>

                <a href="#" class="relative text-gray-700 hover:text-blue-600 transition">
                    <i class="fas fa-shopping-cart text-lg"></i>
                    <span class="absolute -top-2 -right-3 bg-blue-600 text-white text-[10px] font-bold w-5 h-5 flex items-center justify-center rounded-full shadow-md">
                        {{ user.panier.nb_articles|default:0 }}
                    </span>
                </a>

                <button id="logoutBtn" class="btn btn-error btn-sm text-white hover:bg-red-700 transition shadow-sm flex items-center gap-1.5">
                    <i class="fas fa-sign-out-alt text-xs"></i>
                    <span class="hidden sm:inline">Déconnexion</span>
                </button>
            {% else %}
                <button onclick="document.getElementById('login_modal').showModal()" class="btn btn-ghost btn-sm hidden sm:inline-block hover:bg-gray-100">
                    Connexion
                </button>
                <button onclick="document.getElementById('register_modal').showModal()" class="btn btn-sm bg-blue-600 hover:bg-blue-700 text-white shadow-md flex items-center gap-2">
                    <i class="fas fa-user-plus"></i>
                    <span class="hidden sm:inline">Inscription</span>
                </button>
            {% endif %}

            <button id="burgerBtn" class="md:hidden btn btn-ghost btn-sm">
                <i class="fas fa-bars text-xl"></i>
            </button>
        </div>
    </div>

    <!-- Menu mobile -->
    <div id="mobileMenu" class="hidden md:hidden bg-white border-t border-gray-200 p-4 shadow-lg">
        <div class="flex flex-col gap-3 text-gray-600 text-sm">
            <a href="{% url 'home_app:home-page' %}" class="hover:text-blue-600 transition">Accueil</a>
            <a href="{% url 'vehicul_app:list-vehicul' %}" class="hover:text-blue-600 transition">Catalogue</a>
            <a href="#" class="hover:text-blue-600 transition">Financement</a>
            <a href="#" class="hover:text-blue-600 transition">Contact</a>
            <hr>
            <a href="#" class="text-blue-600 font-medium">
                <i class="fas fa-shopping-cart mr-2"></i> Panier ({{ user.panier.nb_articles|default:0 }})
            </a>
        </div>
    </div>
</nav>
<!-- ========== HERO IMMERSIVE (fond fixe) ========== -->
<div class="frame-container">
    <img id="frame" src="{% static 'frames/frame-0001.jpg' %}" alt="">
</div>

<section class="hero-section relative min-h-screen flex items-center justify-center overflow-hidden pt-16">
    <!-- Ta navbar (déjà en fixed, ok) -->
    <!-- Ton contenu hero avec le titre et les boutons -->
    <div class="container mx-auto px-4 text-center text-white relative z-10">
        <h1 class="text-5xl md:text-7xl font-extrabold leading-tight mb-6">
            Votre voiture à crédit.<br>
            <span class="text-blue-200">Vos pièces en ligne.</span>
        </h1>
        <p class="text-xl md:text-2xl text-blue-100 max-w-2xl mx-auto mb-8">
            KOZ Services vous accompagne dans l'achat de votre véhicule...
        </p>
        <div class="flex flex-wrap justify-center gap-4">
            <a href="#" class="btn btn-white btn-lg text-blue-700 hover:bg-blue-50 shadow-lg">
                Découvrir le catalogue
            </a>
            <a href="#" class="btn btn-outline btn-lg text-white border-white/50 hover:bg-white/10">
                Demander un financement
            </a>
        </div>
    </div>
</section>


<!-- ========== SECTION VÉHICULES EN VEDETTE ========== -->
<section class="py-16  bg-gray-50">
    <div class="container  mx-auto px-4">
        <div class="text-center  mb-12">
            <h2 class="text-3xl md:text-4xl font-bold text-gray-800">Nos véhicules en vedette</h2>
            <p class="text-gray-500 mt-2">Découvrez notre sélection de véhicules disponibles</p>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {% for vehicule in vehicules_vedette %}
            <div class="bg-white rounded-2xl shadow-lg overflow-hidden hover:shadow-xl transition group">
                <div class="h-48 overflow-hidden">
                    <img src="{{ vehicule.image_principale.url }}" alt="{{ vehicule.marque.nom }} {{ vehicule.modele }}" class="w-full h-full object-cover group-hover:scale-105 transition duration-500">
                </div>
                <div class="p-4">
                    <h3 class="font-bold text-gray-800">{{ vehicule.marque.nom }} {{ vehicule.modele }}</h3>
                    <p class="text-sm text-gray-500">{{ vehicule.annee }} • {{ vehicule.kilometrage|intcomma }} km</p>
                    <p class="text-lg font-bold text-blue-600 mt-2">{{ vehicule.prix|intcomma }} FCFA</p>
                    <a href="{% url 'vehicul_app:detail-vehicul' vehicule.pk %}" class="btn btn-primary btn-sm w-full mt-3">Voir le détail</a>
                </div>
            </div>
            {% empty %}
            <p class="text-gray-400 col-span-full text-center">Aucun véhicule disponible pour le moment.</p>
            {% endfor %}
        </div>
        <div class="text-center mt-8">
            <a href="{% url 'vehicul_app:list-vehicul' %}" class="btn btn-outline btn-primary">Voir tout le catalogue</a>
        </div>
    </div>
</section>

<!-- ========== SECTION PRODUITS EN VEDETTE ========== -->
<section class="py-16 bg-white">
    <div class="container mx-auto px-4">
        <div class="text-center mb-12">
            <h2 class="text-3xl md:text-4xl font-bold text-gray-800">Pièces et accessoires</h2>
            <p class="text-gray-500 mt-2">L'équipement qu'il vous faut pour votre véhicule</p>
        </div>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            {% for produit in produits_vedette %}
            <div class="bg-gray-50 rounded-xl p-4 text-center hover:shadow-md transition">
                <div class="w-full h-32 bg-gray-200 rounded-lg mb-3 overflow-hidden">
                    <img src="{{ produit.image_principale.url }}" alt="{{ produit.nom }}" class="w-full h-full object-cover">
                </div>
                <h4 class="font-semibold text-gray-800">{{ produit.nom }}</h4>
                <p class="text-blue-600 font-bold">{{ produit.prix|intcomma }} FCFA</p>
                <button class="btn btn-primary btn-sm w-full mt-2">Ajouter au panier</button>
            </div>
            {% empty %}
            <p class="text-gray-400 col-span-full text-center">Aucun produit disponible.</p>
            {% endfor %}
        </div>
    </div>
</section>

<!-- ========== CTA FINAL ========== -->
<section class="py-16 bg-gradient-to-r from-blue-700 to-indigo-800 text-white">
    <div class="container mx-auto px-4 text-center">
        <h2 class="text-3xl md:text-4xl font-bold mb-4">Prêt à rouler avec KOZ ?</h2>
        <p class="text-blue-100 text-lg mb-6">Créez votre compte et faites votre demande de financement en quelques minutes.</p>
        <button onclick="document.getElementById('register_modal').showModal()" class="btn btn-white btn-lg text-blue-700 hover:bg-blue-50 shadow-lg">
            <i class="fas fa-user-plus mr-2"></i> Créer un compte
        </button>
    </div>
</section>

<!-- ========== FOOTER ========== -->
<footer class="bg-gray-800 text-gray-400 py-8">
    <div class="container mx-auto px-4 text-center text-sm">
        <p>&copy; {% now "Y" %} KOZ Services. Tous droits réservés.</p>
        <p class="mt-1">Conçu avec ❤️ pour les passionnés d'automobile.</p>
    </div>
</footer>

<!-- ========== MODALES ========== -->
{% include 'modals/home/register.html' %}
{% include 'modals/home/login.html' %}

<!-- ========== SCRIPTS ========== -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/js/all.min.js"></script>
<script src="{% static 'js/home/register.js' %}"></script>
<script src="{% static 'js/home/login.js' %}"></script>
<script src="{% static 'js/home/logout.js' %}"></script>

<script>
    gsap.registerPlugin(ScrollTrigger);

    const totalFrames = 120;
    const basePath = "{% static 'frames/frame-' %}";
    const frameImg = document.getElementById('frame');

    ScrollTrigger.create({
        trigger: ".hero-section",   // ← Le déclencheur
        start: "top top",           // Début du scroll
        end: "bottom bottom",       // Fin du scroll
        scrub: 0.8,
        onUpdate: (self) => {
            let frameIndex = Math.floor(self.progress * (totalFrames - 1)) + 1;
            frameIndex = Math.min(frameIndex, totalFrames);
            const paddedIndex = String(frameIndex).padStart(4, '0');
            frameImg.src = `${basePath}${paddedIndex}.jpg`;
        }
    });

    // Faire apparaître les sections avec un fondu
const sections = document.querySelectorAll('.fade-section');
sections.forEach((section, index) => {
    gsap.from(section, {
        scrollTrigger: {
            trigger: section,
            start: "top 80%",
            toggleActions: "play none none none"
        },
        opacity: 0,
        y: 50,
        duration: 1,
        delay: index * 0.15
    });
});
</script>

<script>
    // Burger menu
    document.getElementById('burgerBtn')?.addEventListener('click', function() {
        document.getElementById('mobileMenu').classList.toggle('hidden');
    });
</script>

</body>
</html>







{% load static %}
{% load tailwind_tags %}
{% load humanize %}
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
    {% tailwind_css %}
    <title>KOZ Services - Votre voiture à crédit, vos pièces en ligne</title>
    <link rel="stylesheet" href="https://unpkg.com/splitting/dist/splitting.css" />
    <link rel="stylesheet" href="{% static 'css/home/home_style.css' %}">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
</head>
<body>

<!-- ========== NAVBAR ========== -->
<nav class="navbar bg-white/80 backdrop-blur-md shadow-sm fixed top-0 z-50 w-full border-b border-gray-200/40">
    <div class="container mx-auto px-4 flex justify-between items-center h-16">
        
        <!-- Logo -->
        <div class="flex items-center gap-3">
            <a href="{% url 'home_app:home-page' %}" class="flex items-center gap-2">
                <div class="w-10 h-10 bg-gradient-to-br from-blue-600 to-blue-800 rounded-xl flex items-center justify-center shadow-md">
                    <img src="{% static 'images/koz_logo_noBack.png' %}" alt="KOZ" class="w-8 h-8 object-contain">
                </div>
                <span class="text-xl font-bold text-gray-800 hidden sm:inline">KOZ Services</span>
            </a>
        </div>

        <!-- Liens centraux -->
        <div class="hidden md:flex gap-6 text-gray-600 font-medium text-sm">
            <a href="{% url 'home_app:home-page' %}" class="hover:text-blue-600 transition">Accueil</a>
            <a href="{% url 'vehicul_app:list-vehicul' %}" class="hover:text-blue-600 transition">Catalogue</a>
            <a href="#" class="hover:text-blue-600 transition">Financement</a>
            <a href="#" class="hover:text-blue-600 transition">Contact</a>
        </div>

        <!-- Actions -->
        <div class="flex items-center gap-4">
            {% if user.is_authenticated %}
                <a href="{% url 'client_app:client-view' %}" class="hidden sm:flex items-center gap-2 text-sm text-gray-700 hover:text-blue-600 transition font-medium">
                    <i class="fas fa-user-circle text-lg text-blue-600"></i>
                    {{ user.nom_complet }}
                </a>

                <a href="#" class="relative text-gray-700 hover:text-blue-600 transition">
                    <i class="fas fa-shopping-cart text-lg"></i>
                    <span class="absolute -top-2 -right-3 bg-blue-600 text-white text-[10px] font-bold w-5 h-5 flex items-center justify-center rounded-full shadow-md">
                        {{ user.panier.nb_articles|default:0 }}
                    </span>
                </a>

                <button id="logoutBtn" class="btn btn-error btn-sm text-white hover:bg-red-700 transition shadow-sm flex items-center gap-1.5">
                    <i class="fas fa-sign-out-alt text-xs"></i>
                    <span class="hidden sm:inline">Déconnexion</span>
                </button>
            {% else %}
                <button onclick="document.getElementById('login_modal').showModal()" class="btn btn-ghost btn-sm hidden sm:inline-block hover:bg-gray-100">
                    Connexion
                </button>
                <button onclick="document.getElementById('register_modal').showModal()" class="btn btn-sm bg-blue-600 hover:bg-blue-700 text-white shadow-md flex items-center gap-2">
                    <i class="fas fa-user-plus"></i>
                    <span class="hidden sm:inline">Inscription</span>
                </button>
            {% endif %}

            <button id="burgerBtn" class="md:hidden btn btn-ghost btn-sm">
                <i class="fas fa-bars text-xl"></i>
            </button>
        </div>
    </div>

    <!-- Menu mobile -->
    <div id="mobileMenu" class="hidden md:hidden bg-white border-t border-gray-200 p-4 shadow-lg">
        <div class="flex flex-col gap-3 text-gray-600 text-sm">
            <a href="{% url 'home_app:home-page' %}" class="hover:text-blue-600 transition">Accueil</a>
            <a href="{% url 'vehicul_app:list-vehicul' %}" class="hover:text-blue-600 transition">Catalogue</a>
            <a href="#" class="hover:text-blue-600 transition">Financement</a>
            <a href="#" class="hover:text-blue-600 transition">Contact</a>
            <hr>
            <a href="#" class="text-blue-600 font-medium">
                <i class="fas fa-shopping-cart mr-2"></i> Panier ({{ user.panier.nb_articles|default:0 }})
            </a>
        </div>
    </div>
</nav>
<!-- ========== HERO IMMERSIVE (fond fixe) ========== -->
<div class="frame-container">
    <img id="frame" src="{% static 'frames/frame-0001.jpg' %}" alt="">
</div>

<section class="hero-section fade-section relative min-h-screen flex items-center justify-center overflow-hidden pt-16">
    <div class="container mx-auto px-4 text-center text-white relative z-10">
        <h1 class="text-5xl md:text-7xl font-extrabold leading-tight mb-6">
            Votre voiture à crédit.<br>
            <span class="text-blue-200">Vos pièces en ligne.</span>
        </h1>
        <p class="text-xl md:text-2xl text-blue-100 max-w-2xl mx-auto mb-8">
            KOZ Services vous accompagne dans l'achat de votre véhicule, avec des solutions de financement simples et rapides.
        </p>
        <div class="flex flex-wrap justify-center gap-4">
            <a href="#" class="btn btn-white btn-lg text-blue-700 hover:bg-blue-50 shadow-lg">
                Découvrir le catalogue
            </a>
            <a href="#" class="btn btn-outline btn-lg text-white border-white/50 hover:bg-white/10">
                Demander un financement
            </a>
        </div>

        <!-- ========== TEXTE QUI SE DÉVOILE ========== -->
        <div class="mt-16 max-w-3xl mx-auto">
            <p class="text-lg text-blue-100/80 font-light reveal-text" data-splitting>
                Des véhicules de qualité, un financement accessible, un accompagnement personnalisé.
                <br><span class="text-blue-200 font-medium">KOZ Services, votre partenaire automobile.</span>
            </p>
        </div>
    </div>
</section>

<!-- ========== CONTENU SUIVANT (scrollable) ========== -->
<div class="relative z-10 bg-white">

    <!-- ========== SECTION VÉHICULES EN VEDETTE ========== -->
    <section class=" py-16 section-vehicule fade-section ">
       
        <div class="container  mx-auto px-4">
        <div class="text-center  mb-12">
            <h2 class="text-3xl md:text-4xl font-bold text-gray-800">Nos véhicules en vedette</h2>
            <p class="text-gray-500 mt-2">Découvrez notre sélection de véhicules disponibles</p>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {% for vehicule in vehicules_vedette %}
            <div class="bg-white rounded-2xl shadow-lg overflow-hidden hover:shadow-xl transition group">
                <div class="h-48 overflow-hidden">
                    <img src="{{ vehicule.image_principale.url }}" alt="{{ vehicule.marque.nom }} {{ vehicule.modele }}" class="w-full h-full object-cover group-hover:scale-105 transition duration-500">
                </div>
                <div class="p-4">
                    <h3 class="font-bold text-gray-800">{{ vehicule.marque.nom }} {{ vehicule.modele }}</h3>
                    <p class="text-sm text-gray-500">{{ vehicule.annee }} • {{ vehicule.kilometrage|intcomma }} km</p>
                    <p class="text-lg font-bold text-blue-600 mt-2">{{ vehicule.prix|intcomma }} FCFA</p>
                    <a href="{% url 'vehicul_app:detail-vehicul' vehicule.pk %}" class="btn btn-primary btn-sm w-full mt-3">Voir le détail</a>
                </div>
            </div>
            {% empty %}
            <p class="text-gray-400 col-span-full text-center">Aucun véhicule disponible pour le moment.</p>
            {% endfor %}
        </div>
        <div class="text-center mt-8">
            <a href="{% url 'vehicul_app:list-vehicul' %}" class="btn btn-outline btn-primary">Voir tout le catalogue</a>
        </div>
    </div>
    </section>

    <!-- ========== SECTION PRODUITS EN VEDETTE ========== -->
    <section class="py-16 section-produits fade-section bg-white">
     
        <div class="container mx-auto px-4">
        <div class="text-center mb-12">
            <h2 class="text-3xl md:text-4xl font-bold text-gray-800">Pièces et accessoires</h2>
            <p class="text-gray-500 mt-2">L'équipement qu'il vous faut pour votre véhicule</p>
        </div>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            {% for produit in produits_vedette %}
            <div class="bg-gray-50 rounded-xl p-4 text-center hover:shadow-md transition">
                <div class="w-full h-32 bg-gray-200 rounded-lg mb-3 overflow-hidden">
                    <img src="{{ produit.image_principale.url }}" alt="{{ produit.nom }}" class="w-full h-full object-cover">
                </div>
                <h4 class="font-semibold text-gray-800">{{ produit.nom }}</h4>
                <p class="text-blue-600 font-bold">{{ produit.prix|intcomma }} FCFA</p>
                <button class="btn btn-primary btn-sm w-full mt-2">Ajouter au panier</button>
            </div>
            {% empty %}
            <p class="text-gray-400 col-span-full text-center">Aucun produit disponible.</p>
            {% endfor %}
        </div>
        </div>
    </section>
    
    <section class="py-16  fade-section bg-gradient-to-r from-blue-700 to-indigo-800 text-white">
        
         
    </section>

    <!-- ========== FOOTER ========== -->
    <footer class="bg-gray-800 text-gray-400 py-8">
        <div class="container mx-auto px-4 text-center text-sm">
        <p>&copy; {% now "Y" %} KOZ Services. Tous droits réservés.</p>
        <p class="mt-1">Conçu avec ❤️ pour les passionnés d'automobile.</p>
        </div>
    </footer>
</div>

<!-- ========== MODALES ========== -->
{% include 'modals/home/register.html' %}
{% include 'modals/home/login.html' %}

<!-- ========== SCRIPTS ========== -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/js/all.min.js"></script>
<script src="https://unpkg.com/splitting/dist/splitting.min.js"></script>
<script src="{% static 'js/home/register.js' %}"></script>
<script src="{% static 'js/home/login.js' %}"></script>
<script src="{% static 'js/home/logout.js' %}"></script>

<script>
    gsap.registerPlugin(ScrollTrigger);

// ========== 1. HERO FRAMES ==========
const totalFrames = 76;
const basePath = "{% static 'frames/ECO_SYS_PROJECTKoz_Flowsrckoz_flowstaticframesframe-' %}";
const frameImg = document.getElementById('frame');

ScrollTrigger.create({
    trigger: ".hero-section",
    start: "top top",
    end: "bottom bottom",
    scrub: 0.8,
    onUpdate: (self) => {
        let frameIndex = Math.floor(self.progress * (totalFrames - 1)) + 1;
        frameIndex = Math.min(frameIndex, totalFrames);
        const paddedIndex = String(frameIndex).padStart(4, '0');
        frameImg.src = `${basePath}${paddedIndex}.jpg`;
    }
});

// ========== 2. SPLITTING : TEXTE QUI S'ÉCRIT AU SCROLL ==========
let splits = Splitting({ target: '.reveal-text' });

splits.forEach(split => {
    const chars = split.chars;
    
    gsap.from(chars, {
        scrollTrigger: {
            trigger: split.el,
            start: "top 80%",
            toggleActions: "play none none reverse",
        },
        opacity: 0,
        y: 40,
        rotationX: -20,
        duration: 1.2,
        ease: "back.out(1.7)",
        stagger: {
            amount: 1.2,
            from: "start"
        }
    });
});

// ========== 3. FADE-IN DES SECTIONS ==========
const sections = document.querySelectorAll('.fade-section');
sections.forEach((section, index) => {
    gsap.from(section, {
        scrollTrigger: {
            trigger: section,
            start: "top 80%",
            toggleActions: "play none none none",
        },
        opacity: 0,
        y: 60,
        duration: 1,
        delay: index * 0.15,
        ease: "power3.out"
    });
});
</script>

<script>
    // Burger menu
    document.getElementById('burgerBtn')?.addEventListener('click', function() {
        document.getElementById('mobileMenu').classList.toggle('hidden');
    });
</script>

</body>
</html>