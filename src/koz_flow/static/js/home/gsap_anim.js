        gsap.registerPlugin(ScrollTrigger);

        // Faire apparaître les sections avec un fondu
        const sections = document.querySelectorAll(".fade-section-actualité");
        sections.forEach((section, index) => {
            gsap.from(section, {
                scrollTrigger: {
                    trigger: section,
                    start: "top 80%",
                    toggleActions: "play none none reverse"
                },
                opacity: 0,
                y: 50,
                duration: 1,
                delay: index * 0.15
            });
        });

        

        gsap.from(".fade-text",  {
                scrollTrigger: {
                    trigger: ".services-section",
                    start: "top -210%",
                    end: "top -150%",
                    toggleActions: "play none none reverse"
                },
                opacity: 0,
                y: 100,
                duration: 1,
            
            });

        gsap.from(".services-contain",  {
                scrollTrigger: {
                    trigger: ".services-section",
                    start: "top -230%",
                    end: "top -150%",
                    toggleActions: "play none none reverse"
                },
                opacity: 0,
                y: 100,
                duration: 1,
            
            });

        gsap.from(".fade-section", {
                scrollTrigger: {
                    trigger: ".fade-section",
                    start: "top -500%",
                    end: "top -150%",
                    toggleActions: "play none none reverse",
                   
                },
                opacity: 0,
                y: 100,
                duration: 1,
            
            });

        gsap.from(".fade-hero-contain", {
                scrollTrigger: {
                    trigger: ".hero-section",
                    toggleActions: "play none none reverse"
                },
                opacity: 0,
                y: 100,
                duration: 1.5,
            
            });


        // NAVBAR PREMIUM
        // ============================================
        const navbar = document.querySelector('.navbar');

        // 1. Apparition au scroll (pure JS)
        window.addEventListener('scroll', () => {
            if (window.scrollY > 30) {
                navbar.classList.add('visible');
            } else {
                navbar.classList.remove('visible');
            }
            
            // Fond qui s'intensifie
            if (window.scrollY > 200) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });

        // 2. Survol (pour rendre plus réactif)
        navbar.addEventListener('mouseenter', () => {
            navbar.classList.add('visible');
        });

        navbar.addEventListener('mouseleave', () => {
            navbar.classList.remove('visible');
        });


        // ============================================
        // BOXES LATÉRALES : apparition au scroll
        // ============================================
        gsap.registerPlugin(ScrollTrigger);

        // Box 1 : vient de gauche
        gsap.from(".box-left", {
            scrollTrigger: {
                trigger: ".trigger-box",
                start: "top 50%" ,
                end: "top 10%",
                scrub: 1.2,
                toggleActions: "play none none reverse",
                id: "box-left"
            },
            x: -300,
            opacity: 0,
            rotationY: 8,
            duration: 1.5,
            ease: "power3.out"
            
        });

        // Box 2 : vient de droite
        gsap.from(".box-right", {
            scrollTrigger: {
                trigger: ".trigger-box",
                start: "top 30%",
                end: "bottom",
                scrub: 1.2,
                toggleActions: "play none none reverse",
                id: "box-right"
            },
            x: 300,
            opacity: 0,
            rotationX: 8,
            duration: 1.5,
            ease: "power3.out",
            

        });

        // Box 3 : vient du bas
        gsap.from(".box-bottom", {
            scrollTrigger:{
                trigger: ".box-right",
                start: "top 50%",
                end:"bottom 50%",
                scrub: 1.2,
                toggleActions: "play none none reverse",
                id: "box-bottom"

            },
            y: 300,
            opacity: 0,
            rotationX: 8,
            duration: 1.5,
            ease: "power3.out",
        });


        // GSAP text-nouveau et details
        gsap.from(".text-nouveau", {
                    scrollTrigger:{
                        trigger: ".campaign-card",
                        start: "top 65%",
                        end: "top 45%",
                        toggleActions: "play none none reverse",
                    },
                    opacity: 0,
                    x: 300,
                    duration: 2,
                    ease: "power3.out"
                });


        // --- ÉTAPE 2 : PIN DE LA SECTION (le scroll reste bloqué) ---
        ScrollTrigger.create({
            trigger: ".pin-trigger",
            start: "top 9%",
            end: "+=300%",  // La section reste "épinglée" pendant 300% de la hauteur d'écran
            pin: true,
            pinSpacing: true,

        });


                
        // ============================================
        // CARTES ACTUALITÉS : apparition au scroll
        // ============================================
        // 2. Définir campaignCards
        const campaignCards = document.querySelectorAll('.campaign-card');
                gsap.from('.campaign-card',{
                    scrollTrigger: {
                        trigger: ".actualite-containt",
                        start: "top 60%",
                        end: "top 50%",
                        toggleActions: "play none none reverse",
                    },
                    opacity: 0,
                    x: -300,
                    duration: 1.5,
                    ease: "power3.out"
                });
        
            // Animation de survol supplémentaire (flottement)
            campaignCards.forEach(card => {
                card.addEventListener('mouseenter', () => {
                    gsap.to(card, {
                        y: -8,
                        duration: 0.4,
                        ease: "power2.out"
                    });
                });
                card.addEventListener('mouseleave', () => {
                    gsap.to(card, {
                        y: 0,
                        duration: 0.4,
                        ease: "power2.out"
                    });
                });
            });




gsap.registerPlugin(ScrollTrigger);

        // 1️⃣ Splitting pour découper les caractères
       let selection = Splitting();
        console.log(selection)
        // 2️⃣ Animation GSAP
        gsap.from(selection[0].chars, {
            y : 100,
            scaleY:0,
            rotation: 90,
            color: "rgb(255,255,255)",
            stagger: 0.05,
            opacity:0,
            scrollTrigger:{
                trigger :".pin-trigger",
                start :"top 9%",
                end: '+=250%',
                scrub: true,
            }
            
        });

// ============================================================
// SERVICES – PINNED SCROLL ANIMATION
// ============================================================
document.addEventListener('DOMContentLoaded', function() {
    
    gsap.registerPlugin(ScrollTrigger);

    const services = document.querySelectorAll('.service-item');
    const totalServices = services.length;
    
    if (totalServices === 0) return;
    console.log('Total services:', totalServices);

    // Éléments à mettre à jour
    const mainImage = document.getElementById('services-main-image');
    const step = document.getElementById('services-step');
    const typeBadge = document.getElementById('services-type-badge');
    const title = document.getElementById('services-title');
    const description = document.getElementById('services-description');
    const price = document.getElementById('services-price');
    const link = document.querySelector('.services-link');
    const dots = document.querySelectorAll('.services-dot');

    // 1️⃣ Récupérer les données du premier service
    const firstData = services[0]?.querySelector('.service-item-data');
    if (firstData) {
        mainImage.src = firstData.dataset.image;
        step.textContent = `01 / ${String(totalServices).padStart(2, '0')}`;
        typeBadge.textContent = `${firstData.dataset.type}`;
        title.textContent = firstData.dataset.title;
        description.textContent = firstData.dataset.description;
        price.textContent = firstData.dataset.price;
        if (link) link.href = firstData.dataset.link;
    }

    // ============================================================
    // 2️⃣ PIN TRIGGER : la section reste fixe
    // ============================================================
    ScrollTrigger.create({
        trigger: ".services-section",
        start: "top 8%",
        end: "+=300%",  // ← Plus de hauteur pour voir tous les services
        pin: true,
        pinSpacing: true,
        // ← Passe à false après test
    });

    // ============================================================
    // 3️⃣ UPDATE TRIGGERS : chaque service change le contenu
    // ============================================================
    services.forEach((service, index) => {
        const data = service.querySelector('.service-item-data');
        if (!data) return;

        ScrollTrigger.create({
            trigger: service,  // ← LE SERVICE, PAS LE LIEN !
            start: "top center",
            end: "center center",
            onEnter: () => updateService(index),
            onEnterBack: () => updateService(index),
           
            
        }
      
    );


    });

    // ============================================================
    // 4️⃣ FONCTION DE MISE À JOUR
    // ============================================================
    function updateService(index) {
        const data = services[index].querySelector('.service-item-data');
        if (!data) return;

        // Mettre à jour l'image avec fade
        gsap.to(mainImage, {
            opacity: 0,
            duration: 0.4,
            onComplete: () => {
                mainImage.src = data.dataset.image;
                gsap.to(mainImage, { opacity: 1, duration: 0.4 });
            }
        });

        // Mettre à jour les textes
        step.textContent = `${String(index + 1).padStart(2, '0')} / ${String(totalServices).padStart(2, '0')}`;
        typeBadge.textContent = `🔧 ${data.dataset.type}`;
        title.textContent = data.dataset.title;
        description.textContent = data.dataset.description;
        price.textContent = data.dataset.price;
        if (link) link.href = data.dataset.link;

        // Mettre à jour les dots
        dots.forEach((dot, i) => {
            dot.classList.toggle('active', i === index);
        });
    }
});


// ============================================================
// ANIMATION : TYPES DE VÉHICULES (ESCALIER PREMIUM)
// ============================================================
document.addEventListener('DOMContentLoaded', function() {

   
    gsap.registerPlugin(ScrollTrigger);


     // ============================================================
    // 2️⃣ PIN TRIGGER : la section reste fixe
    // ============================================================
   // ScrollTrigger.create({
      //  trigger: ".section_type_vehicul",
      //  start: "top 8%",
       // end: "+=80%",  // ← Plus de hauteur pour voir tous les services
     //   pin: true,
     //   pinSpacing: true,
        // ← Passe à false après test
   // });
    

    // ===== SUV (vient de la gauche) =====
    gsap.from(".suv", {
        x: -200,           // Vient de la gauche
        opacity: 0,
        scale: 0.8,
        rotation: -8,      // Légère rotation
        duration: 1.2,
        ease: "power3.out",
        scrollTrigger: {
            trigger: ".suv",
            start: "top 85%",
            end: "top 40%",
            toggleActions: "play none none reverse",
              // ← Passe à false après test
        }
    });

    // ===== BERLINE (vient du centre) =====
    gsap.from(".berline", {
        y: 80,             // Monte du bas
        opacity: 0,
        scale: 0.9,
        rotation: 2,
        duration: 1.2,
        delay: 0.15,       // Un peu après le SUV
        ease: "power3.out",
        scrollTrigger: {
            trigger: ".berline",
            start: "center 85%",
            end: "top 40%",
            toggleActions: "play none none reverse",
            
        }
    });

    // ===== TRUCK (vient de la droite) =====
    gsap.from(".truck", {
        x: 200,            // Vient de la droite
        opacity: 0,
        scale: 0.8,
        rotation: 8,
        duration: 1.2,
        delay: 0.3,        // Dernier à apparaître
        ease: "power3.out",
        scrollTrigger: {
            trigger: ".truck",
            start: "bottom 85%",
            end: "top 40%",
            toggleActions: "play none none reverse",
            
        }
    });

     gsap.from(".text-anim",{
            x: -150,
            opacity: 0,
            duration: 1.2,
            ease: "power3.out",
        scrollTrigger: {
            trigger: ".truck",
            start: "bottom 80%",
            end: "top 40%",
            toggleActions: "play none none reverse",
            
        }

    });

     gsap.from(".fleche_anim",{
            x: -400,
            opacity: 0,
            duration: 1.5,
            ease: "power3.out",
        scrollTrigger: {
            trigger: ".truck",
            start: "bottom 80%",
            end: "top 40%",
            toggleActions: "play none none reverse",
           
        }

    });

});

// ============================================================
// ANIMATION : GALLERY DE VÉHICULES VEDETTE
// ============================================================
document.addEventListener('DOMContentLoaded', function() {
    gsap.from(".fade-gallery", {
                scrollTrigger: {
                    trigger: ".section_vehicule_vedette",
                    start: "top 60%",
                    end: "top 40%",
                    toggleActions: "play none none reverse", 
                },
                opacity: 0,
                y: 100,
                duration: 1,
            
            });

});

// ============================================================
// STAT ANIME – COUNTER ANIMATION
// ============================================================
document.addEventListener('DOMContentLoaded', function() {
    
    const stats = document.querySelectorAll('.stat-number');
    
    if (stats.length === 0) return;
    
    // Fonction d'animation du compteur
    function animateCounter(el) {
        const target = parseInt(el.getAttribute('data-target'));
        const duration = 2000; // 2 secondes
        const startTime = performance.now();
        
        function updateCounter(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3); // easing cubic-out
            
            const currentValue = Math.floor(eased * target);
            el.textContent = currentValue.toLocaleString();
            
            if (progress < 1) {
                requestAnimationFrame(updateCounter);
            } else {
                el.textContent = target.toLocaleString();
            }
        }
        
        requestAnimationFrame(updateCounter);
    }
    
    // Utiliser IntersectionObserver pour déclencher l'animation
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const el = entry.target;
                animateCounter(el);
                observer.unobserve(el); // Une seule fois
            }
        });
    }, { threshold: 0.5 });
    
    stats.forEach(stat => observer.observe(stat));
});



// Initialize a new Lenis instance for smooth scrolling
const lenis = new Lenis();

// Synchronize Lenis scrolling with GSAP's ScrollTrigger plugin
lenis.on('scroll', ScrollTrigger.update);

// Add Lenis's requestAnimationFrame (raf) method to GSAP's ticker
// This ensures Lenis's smooth scroll animation updates on each GSAP tick
gsap.ticker.add((time) => {
  lenis.raf(time * 500); // Convert time from seconds to milliseconds
});

// Disable lag smoothing in GSAP to prevent any delay in scroll animations
gsap.ticker.lagSmoothing(0);
