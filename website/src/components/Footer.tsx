import Link from "next/link";

export default function Footer() {
  return (
    <footer style={{ borderTop: "1px solid var(--glass-border)", padding: "40px 0", textAlign: "center" }}>
      <div className="container">
        <p style={{ color: "var(--secondary)", fontSize: "0.875rem" }}>
          &copy; {new Date().getFullYear()} AutoHeal AI. Open-source under MIT License.
        </p>
        <div style={{ marginTop: "16px", display: "flex", justifyContent: "center", gap: "24px" }}>
          <Link href="https://github.com/autoheal-ai" target="_blank" style={{ color: "var(--secondary)" }} className="hoverable">
            GitHub
          </Link>
          <Link href="https://pypi.org/project/autoheal-ai/" target="_blank" style={{ color: "var(--secondary)" }} className="hoverable">
            PyPI
          </Link>
        </div>
      </div>
    </footer>
  );
}
