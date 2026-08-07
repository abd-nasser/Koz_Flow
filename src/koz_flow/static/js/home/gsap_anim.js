gsap.registerPlugin(ScrollTrigger);

        
        
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


    document.addEventListener('DOMContentLoaded', function() {
    gsap.from(".hero_fade", {
                opacity: 0,
                y: 200,
                duration: 1.5,
            
            });

    });


        // ============================================
        // BOXES LATÉRALES : apparition au scroll
        // ============================================
        

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


        
// ============================================================
// ACTUALITE ANIMATION
// ============================================================
document.addEventListener('DOMContentLoaded', function() {
    gsap.from(".actualite_fade", {
                scrollTrigger: {
                    trigger: ".actualite_sec",
                    start: "top 60%",
                    end: "top 30%",
                    toggleActions: "play none none reverse", 
                    
                },
                opacity: 0,
                y: 100,
                duration: 1,
            
            });

    // ACTUALITE ANIMATION COLONE GAUCHE
    // =============================================

    gsap.from(".actu_video_img",{
                scrollTrigger:{
                    trigger:".actu_video_img",
                    start: "top 70%",
                    end: "top 30%",
                    toggleActions: "play none none reverse", 
                    
                },
                opacity: 0,
                x: -200,
                duration: 1,
            });

    gsap.from(".actu_type", {
                scrollTrigger: {
                    trigger: ".actu_type",
                    start: "top 60%",
                    end: "top 30%",
                    toggleActions: "play none none reverse", 
                    
                },
                opacity: 0,
                x: 100,
                duration: 1,
            
            });

    gsap.from(".actu_vedette",{
                scrollTrigger:{
                    trigger:".actu_vedette",
                    start: "top 65%",
                    end: "top 30%",
                    toggleActions: "play none none reverse", 
                    
                },
                opacity: 0,
                y: 200,
                duration: 1,
            });
    gsap.from(".actu_titre",{
                scrollTrigger:{
                    trigger:".actu_titre",
                    start: "top 90%",
                    end: "top 30%",
                    toggleActions: "play none none reverse", 
                   
                },
                opacity: 0,
                x: -200,
                duration: 1.5,
            });

    gsap.from(".actu_mini_descript",{
                scrollTrigger:{
                    trigger:".actu_titre",
                    start: "top 90%",
                    end: "top 30%",
                    toggleActions: "play none none reverse", 
                    
                },
                opacity: 0,
                y: 200,
                duration: 2,
            });


     // ACTUALITE ANIMATION COLONE DROITE
    // =============================================
    gsap.from(".actu_descript",{
                scrollTrigger:{
                    trigger:".actu_descript",
                    start: "top 71%",
                    end: "top 30%",
                    toggleActions: "play none none reverse", 
                    
                },
                opacity: 0,
                x: 200,
                duration: 1,
            });


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



