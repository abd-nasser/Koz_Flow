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


        // Initialize a new Lenis instance for smooth scrolling
const lenis = new Lenis();

// Synchronize Lenis scrolling with GSAP's ScrollTrigger plugin
lenis.on('scroll', ScrollTrigger.update);

// Add Lenis's requestAnimationFrame (raf) method to GSAP's ticker
// This ensures Lenis's smooth scroll animation updates on each GSAP tick
gsap.ticker.add((time) => {
  lenis.raf(time * 300); // Convert time from seconds to milliseconds
});

// Disable lag smoothing in GSAP to prevent any delay in scroll animations
gsap.ticker.lagSmoothing(0);

  