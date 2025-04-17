document.addEventListener("DOMContentLoaded", () => {
  // Navbar scroll effect
  const navbar = document.querySelector(".navbar")

  window.addEventListener("scroll", () => {
    if (window.scrollY > 50) {
      navbar.classList.add("scrolled")
    } else {
      navbar.classList.remove("scrolled")
    }
  })

  // FAQ Accordion
  const faqItems = document.querySelectorAll(".faq-item")

  faqItems.forEach((item) => {
    const question = item.querySelector(".faq-question")

    question.addEventListener("click", () => {
      // Close all other items
      faqItems.forEach((otherItem) => {
        if (otherItem !== item) {
          otherItem.classList.remove("active")
        }
      })

      // Toggle current item
      item.classList.toggle("active")
    })
  })

  // Mobile Menu Toggle
  const mobileMenuButton = document.createElement("button")
  mobileMenuButton.classList.add("mobile-menu-button")
  mobileMenuButton.innerHTML = `
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <line x1="3" y1="12" x2="21" y2="12"></line>
      <line x1="3" y1="6" x2="21" y2="6"></line>
      <line x1="3" y1="18" x2="21" y2="18"></line>
    </svg>
  `

  const navbar_container = document.querySelector(".navbar .container")
  const navLinks = document.querySelector(".nav-links")

  if (window.innerWidth <= 768) {
    navbar_container.insertBefore(mobileMenuButton, navLinks)

    mobileMenuButton.addEventListener("click", () => {
      navLinks.classList.toggle("active")
    })
  }

  // Smooth scrolling for anchor links
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      e.preventDefault()

      const targetId = this.getAttribute("href")
      if (targetId === "#") return

      const targetElement = document.querySelector(targetId)
      if (targetElement) {
        window.scrollTo({
          top: targetElement.offsetTop - 80, // Adjust for navbar height
          behavior: "smooth",
        })

        // Close mobile menu if open
        if (navLinks.classList.contains("active")) {
          navLinks.classList.remove("active")
        }
      }
    })
  })

  // Add active class to nav links based on scroll position
  const sections = document.querySelectorAll("section[id]")

  function highlightNavLink() {
    const scrollPosition = window.scrollY + 100

    sections.forEach((section) => {
      const sectionTop = section.offsetTop
      const sectionHeight = section.offsetHeight
      const sectionId = section.getAttribute("id")

      if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
        document.querySelector(`.nav-links a[href="#${sectionId}"]`)?.classList.add("active")
      } else {
        document.querySelector(`.nav-links a[href="#${sectionId}"]`)?.classList.remove("active")
      }
    })
  }

  window.addEventListener("scroll", highlightNavLink)

  // Initialize the active nav link on page load
  highlightNavLink()

  // Scroll animations
  const animateOnScroll = () => {
    // Steps animation
    const steps = document.querySelectorAll(".step")
    steps.forEach((step, index) => {
      const stepPosition = step.getBoundingClientRect().top
      const screenPosition = window.innerHeight / 1.3

      if (stepPosition < screenPosition) {
        setTimeout(() => {
          step.classList.add("animate")
        }, index * 200)
      }
    })

    // Benefits animation
    const benefits = document.querySelectorAll(".benefit-card")
    benefits.forEach((benefit, index) => {
      const benefitPosition = benefit.getBoundingClientRect().top
      const screenPosition = window.innerHeight / 1.3

      if (benefitPosition < screenPosition) {
        setTimeout(() => {
          benefit.classList.add("animate")
        }, index * 150)
      }
    })

    // Pricing cards animation
    const pricingCards = document.querySelectorAll(".pricing-card")
    pricingCards.forEach((card, index) => {
      const cardPosition = card.getBoundingClientRect().top
      const screenPosition = window.innerHeight / 1.3

      if (cardPosition < screenPosition) {
        setTimeout(() => {
          card.classList.add("animate")
        }, index * 200)
      }
    })

    // Performers animation
    const performers = document.querySelectorAll(".performer")
    performers.forEach((performer, index) => {
      const performerPosition = performer.getBoundingClientRect().top
      const screenPosition = window.innerHeight / 1.3

      if (performerPosition < screenPosition) {
        setTimeout(() => {
          performer.classList.add("animate")
        }, index * 150)
      }
    })

    // Testimonials animation
    const testimonials = document.querySelectorAll(".testimonial-card")
    testimonials.forEach((testimonial, index) => {
      const testimonialPosition = testimonial.getBoundingClientRect().top
      const screenPosition = window.innerHeight / 1.3

      if (testimonialPosition < screenPosition) {
        setTimeout(() => {
          testimonial.classList.add("animate")
        }, index * 200)
      }
    })

    // FAQ animation
    const faqItems = document.querySelectorAll(".faq-item")
    faqItems.forEach((faq, index) => {
      const faqPosition = faq.getBoundingClientRect().top
      const screenPosition = window.innerHeight / 1.3

      if (faqPosition < screenPosition) {
        setTimeout(() => {
          faq.classList.add("animate")
        }, index * 100)
      }
    })

    // Special features animation
    const specialFeaturesContent = document.querySelector(".special-features-content")
    const specialFeaturesImage = document.querySelector(".special-features-image")

    if (specialFeaturesContent) {
      const contentPosition = specialFeaturesContent.getBoundingClientRect().top
      const screenPosition = window.innerHeight / 1.3

      if (contentPosition < screenPosition) {
        specialFeaturesContent.classList.add("animate")
        specialFeaturesImage.classList.add("animate")
      }
    }

    // CTA section animation
    const ctaSection = document.querySelector(".cta-section")
    if (ctaSection) {
      const ctaPosition = ctaSection.getBoundingClientRect().top
      const screenPosition = window.innerHeight / 1.3

      if (ctaPosition < screenPosition) {
        ctaSection.classList.add("animate")
      }
    }
  }

  // Run animations on scroll
  window.addEventListener("scroll", animateOnScroll)

  // Run animations on page load
  setTimeout(animateOnScroll, 500)

  // Hero image 3D effect
  const heroImage = document.querySelector(".hero-image")

  if (heroImage) {
    document.addEventListener("mousemove", (e) => {
      const xAxis = (window.innerWidth / 2 - e.pageX) / 25
      const yAxis = (window.innerHeight / 2 - e.pageY) / 25

      heroImage.style.transform = `rotateY(${xAxis}deg) rotateX(${yAxis}deg)`
    })

    // Reset on mouse leave
    document.addEventListener("mouseleave", () => {
      heroImage.style.transform = "rotateY(0deg) rotateX(0deg)"
    })
  }

  // Animated counter for pricing
  const animateCounter = (element, target, duration = 2000) => {
    let start = 0
    const increment = target / (duration / 16)

    const updateCounter = () => {
      start += increment
      if (start < target) {
        element.textContent = Math.floor(start)
        requestAnimationFrame(updateCounter)
      } else {
        element.textContent = target
      }
    }

    updateCounter()
  }

  // Animate counters when they come into view
  const priceElements = document.querySelectorAll(".price .amount")

  const observePrices = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const target = Number.parseFloat(entry.target.textContent)
            if (!isNaN(target)) {
              entry.target.textContent = "0"
              animateCounter(entry.target, target)
            }
            observePrices.unobserve(entry.target)
          }
        })
      },
      { threshold: 0.5 },
  )

  priceElements.forEach((price) => {
    observePrices.observe(price)
  })

  // Particle background effect for hero section
  const createParticles = () => {
    const hero = document.querySelector(".hero")

    if (hero) {
      for (let i = 0; i < 50; i++) {
        const particle = document.createElement("div")
        particle.classList.add("particle")

        // Random position
        const posX = Math.random() * 100
        const posY = Math.random() * 100

        // Random size
        const size = Math.random() * 10 + 5

        // Random opacity
        const opacity = Math.random() * 0.5 + 0.1

        // Random animation duration
        const duration = Math.random() * 20 + 10

        // Set styles
        particle.style.cssText = `
          position: absolute;
          top: ${posY}%;
          left: ${posX}%;
          width: ${size}px;
          height: ${size}px;
          background-color: rgba(37, 99, 235, ${opacity});
          border-radius: 50%;
          pointer-events: none;
          animation: float ${duration}s infinite ease-in-out;
        `

        hero.appendChild(particle)
      }
    }
  }

  // Create particles
  createParticles()

  // Auth form enhancements
  const authTabs = document.querySelectorAll(".auth-tab")

  authTabs.forEach((tab) => {
    tab.addEventListener("click", function () {
      // Add a subtle animation when clicking tabs
      this.style.transition = "all 0.3s ease"
      this.style.transform = "scale(0.95)"

      setTimeout(() => {
        this.style.transform = "scale(1)"
      }, 150)
    })
  })

  // Add focus and blur effects to form inputs
  const formInputs = document.querySelectorAll(".auth-form input")

  formInputs.forEach((input) => {
    // Add label animation on focus
    input.addEventListener("focus", function () {
      const label = this.previousElementSibling
      if (label && label.tagName === "LABEL") {
        label.style.color = "var(--primary-color)"
      }
    })

    // Remove label animation on blur
    input.addEventListener("blur", function () {
      const label = this.previousElementSibling
      if (label && label.tagName === "LABEL") {
        label.style.color = ""
      }
    })
  })

  // Add button animation
  const authButtons = document.querySelectorAll(".auth-form button")

  authButtons.forEach((button) => {
    button.addEventListener("mousedown", function () {
      this.style.transform = "scale(0.98)"
    })

    button.addEventListener("mouseup", function () {
      this.style.transform = ""
    })

    button.addEventListener("mouseleave", function () {
      this.style.transform = ""
    })
  })

  // Test results page - download functionality
  const downloadResultsButton = document.getElementById("download-results")
  if (downloadResultsButton) {
    downloadResultsButton.addEventListener("click", () => {
      // Get the test ID from the URL
      const urlParts = window.location.pathname.split("/")
      // Find the test ID (should be the last part before the trailing slash)
      let testId = null
      for (let i = urlParts.length - 1; i >= 0; i--) {
        if (urlParts[i] && urlParts[i] !== "") {
          testId = urlParts[i]
          break
        }
      }

      if (testId) {
        // Redirect to the download URL
        window.location.href = `/ielts-mock/results/${testId}/download/`
      } else {
        console.error("Could not determine test ID from URL")
      }
    })
  }
})
