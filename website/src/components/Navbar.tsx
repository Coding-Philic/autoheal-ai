import Link from "next/link";
import styles from "./Navbar.module.css";
import { Stethoscope } from "lucide-react";

export default function Navbar() {
  return (
    <nav className={styles.navbar}>
      <div className={`container ${styles.navContainer}`}>
        <Link href="/" className={`hoverable ${styles.logo}`}>
          <Stethoscope size={24} color="var(--accent)" />
          <span>AutoHeal AI</span>
        </Link>
        
        <div className={styles.links}>
          <Link href="/" className="hoverable">Home</Link>
          <Link href="/docs" className="hoverable">Docs</Link>
          <Link href="/#how-it-works" className="hoverable">Features</Link>
          <Link href="/#install" className="hoverable">Install</Link>
          <Link href="/#contact" className="hoverable">Contact</Link>
        </div>
      </div>
    </nav>
  );
}
