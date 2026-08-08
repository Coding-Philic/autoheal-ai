"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import SplineBackground from "./SplineBackground";
import styles from "./Hero.module.css";
import { Terminal, ShieldCheck } from "lucide-react";

export default function Hero() {
  const headingRef = useRef<HTMLHeadingElement>(null);
  const subRef = useRef<HTMLParagraphElement>(null);
  const buttonsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const tl = gsap.timeline();
    
    // Text Reveal Animation
    tl.fromTo(headingRef.current, 
      { y: 50, opacity: 0 }, 
      { y: 0, opacity: 1, duration: 1, ease: "power3.out", delay: 0.2 }
    )
    .fromTo(subRef.current,
      { y: 30, opacity: 0 },
      { y: 0, opacity: 1, duration: 0.8, ease: "power3.out" },
      "-=0.6"
    )
    .fromTo(buttonsRef.current,
      { y: 20, opacity: 0 },
      { y: 0, opacity: 1, duration: 0.8, ease: "power3.out" },
      "-=0.6"
    );
  }, []);

  return (
    <section className={styles.heroSection}>
      <SplineBackground />
      
      <div className={`container ${styles.content}`}>
        <div className={styles.badge}>
          <ShieldCheck size={16} />
          <span>AI-Powered Diagnostics</span>
        </div>
        
        <h1 ref={headingRef} className={`h1 ${styles.title}`}>
          We find the problem.<br />
          We build the fix.<br />
          <span className="text-gradient">We prove it works.</span>
        </h1>
        
        <p ref={subRef} className={`p-large ${styles.subtitle}`}>
          AutoHeal AI is a language-agnostic CLI tool that wraps any command, detects errors in real-time, and automatically diagnoses and fixes them.
        </p>
        
        <div ref={buttonsRef} className={styles.buttonGroup}>
          <a href="#install" className="btn-primary hoverable">
            <Terminal size={18} />
            Install AutoHeal
          </a>
          <a href="#how-it-works" className="btn-secondary hoverable">
            See how it works
          </a>
        </div>
      </div>
    </section>
  );
}
