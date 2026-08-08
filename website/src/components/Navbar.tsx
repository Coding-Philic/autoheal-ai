"use client";

import { useState, useEffect, useRef } from "react";
import Link from "next/link";
import styles from "./Navbar.module.css";
import { Stethoscope, Menu, X } from "lucide-react";
import gsap from "gsap";

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const linksRef = useRef<(HTMLAnchorElement | null)[]>([]);

  useEffect(() => {
    if (isOpen) {
      const tl = gsap.timeline();
      
      // 1. Slide menu in from the right
      tl.to(menuRef.current, {
        x: 0,
        duration: 0.7,
        ease: "power4.inOut"
      })
      // 2. Reveal text links
      .to(linksRef.current, {
        y: 0,
        opacity: 1,
        duration: 0.5,
        stagger: 0.1,
        ease: "power3.out"
      }, "-=0.3"); // Overlap slightly with the slide animation
      
    } else {
      const tl = gsap.timeline();
      
      // 1. Hide text links quickly
      tl.to(linksRef.current, {
        y: 20,
        opacity: 0,
        duration: 0.3,
        ease: "power3.in"
      })
      // 2. Slide menu back to the right
      .to(menuRef.current, {
        x: "100%",
        duration: 0.6,
        ease: "power4.inOut"
      }, "-=0.1");
    }
  }, [isOpen]);

  const toggleMenu = () => setIsOpen(!isOpen);
  const closeMenu = () => setIsOpen(false);

  const navLinks = [
    { name: "Home", href: "/" },
    { name: "Docs", href: "/docs" },
    { name: "Features", href: "/#how-it-works" },
    { name: "Install", href: "/#install" },
    { name: "Contact", href: "/#contact" }
  ];

  return (
    <>
      <nav className={styles.navbar}>
        <div className={`container ${styles.navContainer}`}>
          <Link href="/" className={`hoverable ${styles.logo}`} onClick={closeMenu}>
            <Stethoscope size={24} color="var(--accent)" />
            <span>AutoHeal AI</span>
          </Link>
          
          {/* Desktop Links */}
          <div className={styles.links}>
            {navLinks.map((link) => (
              <Link key={link.name} href={link.href} className="hoverable">
                {link.name}
              </Link>
            ))}
          </div>

          {/* Mobile Menu Button */}
          <button 
            className={styles.mobileToggle} 
            onClick={toggleMenu}
            aria-label="Toggle Menu"
          >
            {isOpen ? <X size={28} /> : <Menu size={28} />}
          </button>
        </div>
      </nav>

      {/* Full Screen Blurred Backdrop (behind the drawer) */}
      <div 
        className={`${styles.mobileBackdrop} ${isOpen ? styles.backdropOpen : ""}`}
        onClick={closeMenu}
      />

      {/* Mobile Menu Overlay (Always rendered, controlled by GSAP) */}
      <div className={styles.mobileMenu} ref={menuRef}>
        <div className={styles.mobileMenuContent}>
          {navLinks.map((link, idx) => (
            <Link 
              key={link.name} 
              href={link.href} 
              onClick={closeMenu}
              ref={(el) => { linksRef.current[idx] = el; }}
            >
              {link.name}
            </Link>
          ))}
        </div>
      </div>
    </>
  );
}
