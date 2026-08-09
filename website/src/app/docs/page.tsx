"use client";

import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import styles from "./Docs.module.css";
import { useEffect, useRef, useState } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import {
  Terminal,
  ShieldCheck,
  Cpu,
  Database,
  RefreshCw,
  Zap,
  ChevronRight,
  Settings,
  Book,
  AlertTriangle,
  CheckCircle,
  Package,
  Key,
  Play,
  Eye,
  History,
  Info,
} from "lucide-react";

/* ─────────────────────────────────────────
   Sidebar navigation sections
───────────────────────────────────────── */
const navSections = [
  { id: "what-is-autoheal", label: "What Is AutoHeal?" },
  { id: "quick-start",      label: "Quick Start" },
  { id: "how-it-works",     label: "How It Works" },
  { id: "behind-the-scenes",label: "Behind the Scenes" },
  { id: "cli-commands",     label: "CLI Commands" },
  { id: "configuration",    label: "Configuration" },
  { id: "llm-providers",    label: "LLM Providers" },
  { id: "integrating",      label: "Integrating Projects" },
  { id: "faq",              label: "FAQ" },
];

/* ─────────────────────────────────────────
   Liquid / Blob interactive background
───────────────────────────────────────── */
function LiquidBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let W = (canvas.width  = window.innerWidth);
    let H = (canvas.height = window.innerHeight);
    let mouse = { x: W / 2, y: H / 2 };
    let animId: number;

    /* Metaball blobs */
    const blobs = Array.from({ length: 6 }, (_, i) => ({
      x: Math.random() * W,
      y: Math.random() * H,
      vx: (Math.random() - 0.5) * 0.4,
      vy: (Math.random() - 0.5) * 0.4,
      r: 180 + Math.random() * 160,
      hue: [220, 230, 200, 210, 240, 225][i],
    }));

    const onMove = (e: MouseEvent) => {
      mouse.x = e.clientX;
      mouse.y = e.clientY;
    };
    const onTouch = (e: TouchEvent) => {
      mouse.x = e.touches[0].clientX;
      mouse.y = e.touches[0].clientY;
    };

    window.addEventListener("mousemove", onMove);
    window.addEventListener("touchmove", onTouch, { passive: true });

    const resize = () => {
      W = canvas.width  = window.innerWidth;
      H = canvas.height = window.innerHeight;
    };
    window.addEventListener("resize", resize);

    function draw() {
      if (!ctx) return;
      ctx.clearRect(0, 0, W, H);

      blobs.forEach((b) => {
        /* Gentle drift */
        b.x += b.vx;
        b.y += b.vy;
        if (b.x < -b.r) b.x = W + b.r;
        if (b.x > W + b.r) b.x = -b.r;
        if (b.y < -b.r) b.y = H + b.r;
        if (b.y > H + b.r) b.y = -b.r;

        /* Mouse attraction — subtle */
        const dx = mouse.x - b.x;
        const dy = mouse.y - b.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 600) {
          b.vx += (dx / dist) * 0.012;
          b.vy += (dy / dist) * 0.012;
        }

        /* Speed damping */
        b.vx *= 0.97;
        b.vy *= 0.97;

        /* Draw blob */
        const grad = ctx.createRadialGradient(b.x, b.y, 0, b.x, b.y, b.r);
        grad.addColorStop(0, `hsla(${b.hue}, 60%, 40%, 0.14)`);
        grad.addColorStop(0.5, `hsla(${b.hue}, 55%, 30%, 0.06)`);
        grad.addColorStop(1, `hsla(${b.hue}, 50%, 20%, 0)`);

        ctx.beginPath();
        ctx.arc(b.x, b.y, b.r, 0, Math.PI * 2);
        ctx.fillStyle = grad;
        ctx.fill();
      });

      animId = requestAnimationFrame(draw);
    }

    draw();

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("touchmove", onTouch);
      window.removeEventListener("resize", resize);
    };
  }, []);

  return <canvas ref={canvasRef} className={styles.liquidCanvas} />;
}

/* ─────────────────────────────────────────
   Code Block component
───────────────────────────────────────── */
function CodeBlock({ children, label }: { children: string; label?: string }) {
  const [copied, setCopied] = useState(false);

  const copy = () => {
    navigator.clipboard.writeText(children.trim());
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className={styles.codeWrapper}>
      {label && <span className={styles.codeLabel}>{label}</span>}
      <button className={styles.copyBtn} onClick={copy} aria-label="Copy code">
        {copied ? <CheckCircle size={14} /> : "copy"}
      </button>
      <pre><code>{children}</code></pre>
    </div>
  );
}

/* ─────────────────────────────────────────
   Step card
───────────────────────────────────────── */
function StepCard({ n, icon, title, children }: { n: number; icon: React.ReactNode; title: string; children: React.ReactNode }) {
  return (
    <div className={styles.stepCard}>
      <div className={styles.stepMeta}>
        <span className={styles.stepNum}>{n}</span>
        <div className={styles.stepIcon}>{icon}</div>
      </div>
      <div className={styles.stepBody}>
        <h3>{title}</h3>
        {children}
      </div>
    </div>
  );
}

/* ─────────────────────────────────────────
   Main Docs Page
───────────────────────────────────────── */
export default function Docs() {
  const [activeSection, setActiveSection] = useState("what-is-autoheal");

  /* GSAP scroll animations */
  useEffect(() => {
    gsap.registerPlugin(ScrollTrigger);

    const cards = gsap.utils.toArray<HTMLElement>(`.${styles.animCard}`);
    cards.forEach((card) => {
      gsap.fromTo(
        card,
        { y: 40, opacity: 0 },
        {
          y: 0,
          opacity: 1,
          duration: 0.7,
          ease: "power3.out",
          scrollTrigger: {
            trigger: card,
            start: "top 85%",
            toggleActions: "play none none reverse",
          },
        }
      );
    });

    /* Active sidebar tracking */
    const sectionEls = navSections.map((s) => document.getElementById(s.id));

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) setActiveSection(e.target.id);
        });
      },
      { rootMargin: "-30% 0px -60% 0px" }
    );

    sectionEls.forEach((el) => el && observer.observe(el));
    return () => observer.disconnect();
  }, []);

  return (
    <main className={styles.docsPage}>
      {/* Liquid interactive background */}
      <LiquidBackground />

      <Navbar />

      <div className={`container ${styles.layout}`}>
        {/* ── Sidebar ── */}
        <aside className={styles.sidebar}>
          <div className={styles.sidebarSticky}>
            <p className={styles.sidebarLabel}>On this page</p>
            <nav>
              <ul className={styles.sidebarNav}>
                {navSections.map((s) => (
                  <li key={s.id}>
                    <a
                      href={`#${s.id}`}
                      className={`${styles.sidebarLink} ${activeSection === s.id ? styles.sidebarLinkActive : ""} hoverable`}
                    >
                      <ChevronRight size={12} className={styles.sidebarChev} />
                      {s.label}
                    </a>
                  </li>
                ))}
              </ul>
            </nav>
          </div>
        </aside>

        {/* ── Main Content ── */}
        <article className={styles.content}>
          <header className={styles.docHeader}>
            <div className={styles.docBadge}>
              <Book size={14} />
              <span>Documentation</span>
            </div>
            <h1 className={`h1 ${styles.docTitle}`}>AutoHeal AI</h1>
            <p className={`p-large ${styles.docSubtitle}`}>
              Everything you need to install, configure, and understand how
              AutoHeal AI works with your real projects — step by step.
            </p>
          </header>

          {/* ─────────────────── SECTION 1 ─────────────────── */}
          <section id="what-is-autoheal" className={styles.section}>
            <h2>What Is AutoHeal AI?</h2>
            <p className={styles.sectionLead}>
              AutoHeal AI is a <strong>CLI package</strong> — not a website,
              not a cloud service. It's a terminal tool you install with one
              command and attach to any project you're already running.
            </p>

            <div className={`${styles.glassCard} ${styles.animCard}`}>
              <h3>Think of it this way</h3>
              <p>
                Imagine you have a project — a Python API, a Node.js website,
                any app. Right now, when that app crashes, an engineer reads the
                error, understands it, and manually fixes it. That cycle repeats
                forever.
              </p>
              <p style={{ marginTop: 12 }}>
                AutoHeal breaks that cycle. It wraps around your running
                process, watches every line of output, and when an error hits —
                it detects, diagnoses, and fixes it automatically using AI.
                Then it remembers that fix, so the same error never costs you
                time again.
              </p>
            </div>

            <div className={styles.twoCol}>
              <div className={`${styles.glassCard} ${styles.animCard} ${styles.notCard}`}>
                <AlertTriangle size={20} color="#ef4444" />
                <h4>What it is NOT</h4>
                <ul>
                  <li>Not a website or web app</li>
                  <li>Not a cloud service</li>
                  <li>Not something you put inside your code</li>
                  <li>Not a browser tool</li>
                </ul>
              </div>
              <div className={`${styles.glassCard} ${styles.animCard} ${styles.isCard}`}>
                <CheckCircle size={20} color="#22c55e" />
                <h4>What it IS</h4>
                <ul>
                  <li>A CLI command installed via pip</li>
                  <li>A background daemon watching your process</li>
                  <li>Runs entirely in your terminal</li>
                  <li>Works with any language / framework</li>
                </ul>
              </div>
            </div>
          </section>

          {/* ─────────────────── SECTION 2 ─────────────────── */}
          <section id="quick-start" className={styles.section}>
            <h2>Quick Start</h2>
            <p className={styles.sectionLead}>
              Get AutoHeal running in under two minutes.
            </p>

            <StepCard n={1} icon={<Package size={18} />} title="Install AutoHeal">
              <p>Install globally using pip. Works on macOS, Linux, and Windows.</p>
              <CodeBlock label="terminal">{`pip install autoheal-ai

# Verify installation
autoheal version`}</CodeBlock>
            </StepCard>

            <StepCard n={2} icon={<Terminal size={18} />} title="Go to your project">
              <p>
                Navigate to the root folder of the project you want to protect.
                This could be a Python app, a Node.js server, anything.
              </p>
              <CodeBlock label="terminal">{`cd /path/to/your-project

# Example: a web project
cd ~/projects/my-website`}</CodeBlock>
            </StepCard>

            <StepCard n={3} icon={<Zap size={18} />} title="Initialize AutoHeal">
              <p>
                This scans your project, creates the <code>.autoheal/</code>{" "}
                folder with a default config, and sets up the error memory
                database.
              </p>
              <CodeBlock label="terminal">{`autoheal init`}</CodeBlock>
              <div className={`${styles.infoBox} ${styles.animCard}`}>
                <Info size={15} />
                <span>
                  AutoHeal auto-detects your language and framework. It never
                  modifies your existing code during init.
                </span>
              </div>
            </StepCard>

            <StepCard n={4} icon={<Key size={18} />} title="Set your LLM provider">
              <p>
                AutoHeal uses an AI model to understand and fix errors. Choose
                your provider and add your API key.
              </p>
              <CodeBlock label="terminal — Google Gemini (free)">{`autoheal config set llm.provider google
autoheal config set llm.model gemini-2.0-flash
autoheal config set llm.api_key YOUR_GOOGLE_API_KEY`}</CodeBlock>
              <CodeBlock label="terminal — OpenAI">{`autoheal config set llm.provider openai
autoheal config set llm.api_key sk-proj-your-key`}</CodeBlock>
              <CodeBlock label="terminal — No internet (local Ollama)">{`autoheal config set llm.provider ollama
autoheal config set llm.model llama3.1`}</CodeBlock>
            </StepCard>

            <StepCard n={5} icon={<Play size={18} />} title="Run your project with monitoring">
              <p>
                Replace your normal start command with{" "}
                <code>autoheal run "..."</code>. Everything else stays the same.
              </p>
              <CodeBlock label="terminal">{`# Python project
autoheal run "python app.py"

# Node.js project
autoheal run "node server.js"
autoheal run "npm start"

# Any command
autoheal run "your-normal-start-command"`}</CodeBlock>
            </StepCard>
          </section>

          {/* ─────────────────── SECTION 3 ─────────────────── */}
          <section id="how-it-works" className={styles.section}>
            <h2>How It Works</h2>
            <p className={styles.sectionLead}>
              AutoHeal sits beside your project as a wrapper. Your code runs
              unchanged — AutoHeal observes it from the outside.
            </p>

            {/* Architecture visual */}
            <div className={`${styles.archDiagram} ${styles.animCard}`}>
              <div className={styles.archCol}>
                <div className={styles.archGroup}>
                  <span className={styles.archGroupLabel}>Your Terminal</span>
                  <div className={styles.archCommand}>
                    <Terminal size={14} />
                    <code>autoheal run "python app.py"</code>
                  </div>
                </div>
              </div>

              <div className={styles.archPipeline}>
                {[
                  { icon: <Eye size={16} />, name: "Sentinel", sub: "detects errors" },
                  { icon: <Cpu size={16} />, name: "CECE", sub: "captures context" },
                  { icon: <Database size={16} />, name: "Memory", sub: "pattern lookup" },
                  { icon: <Zap size={16} />, name: "Diagnostics", sub: "AI root cause" },
                  { icon: <Settings size={16} />, name: "Resolution", sub: "generate fix" },
                  { icon: <ShieldCheck size={16} />, name: "Harness", sub: "validate safely" },
                  { icon: <RefreshCw size={16} />, name: "Apply", sub: "fix + restart" },
                ].map((node, i, arr) => (
                  <div className={styles.archNodeWrap} key={node.name}>
                    <div className={styles.archNode}>
                      <div className={styles.archNodeIcon}>{node.icon}</div>
                      <div className={styles.archNodeText}>
                        <strong>{node.name}</strong>
                        <small>{node.sub}</small>
                      </div>
                    </div>
                    {i < arr.length - 1 && (
                      <ChevronRight size={14} className={styles.archArrow} />
                    )}
                  </div>
                ))}
              </div>
            </div>

            <div className={styles.stepsList}>
              {[
                { icon: <Eye size={16} />, title: "Sentinel Agent", desc: "Wraps your process as a child process, reads every line of stdout and stderr in real-time, detects known error patterns (TypeError, ImportError, etc.)." },
                { icon: <Cpu size={16} />, title: "CECE Engine", desc: "Captures full context — stack trace, file location, line number, environment info (Python version, OS, memory usage), and recent system state." },
                { icon: <Database size={16} />, title: "Memory Store", desc: "Checks if this error type has been seen before. If similarity is above 90%, it applies the known fix instantly — no AI call needed, under 200ms." },
                { icon: <Zap size={16} />, title: "Diagnostics Engine", desc: "For new errors, sends the full context to your LLM (Gemini, GPT-4o, etc.). The AI returns a root cause explanation and a confidence score." },
                { icon: <Settings size={16} />, title: "Resolution Engine", desc: "Picks a fix strategy based on confidence: restart process (low risk), change config, apply code patch, install dependency, or escalate to you." },
                { icon: <ShieldCheck size={16} />, title: "Harness Controller", desc: "Tests the fix in a sandboxed subprocess first. Only if it passes does AutoHeal apply it to your real project. Creates a git backup before any code change." },
                { icon: <RefreshCw size={16} />, title: "Apply & Learn", desc: "Fix is applied, your app restarts. AutoHeal monitors for 60 seconds. The resolution is saved to the memory database — same error = instant fix next time." },
              ].map((step, i) => (
                <div className={`${styles.workStep} ${styles.animCard}`} key={i}>
                  <div className={styles.workStepIcon}>{step.icon}</div>
                  <div>
                    <h4>{step.title}</h4>
                    <p>{step.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* ─────────────────── SECTION 4 ─────────────────── */}
          <section id="behind-the-scenes" className={styles.section}>
            <h2>Behind the Scenes</h2>
            <p className={styles.sectionLead}>
              What actually happens the moment an error occurs in your project.
            </p>

            <div className={`${styles.timelineCard} ${styles.animCard}`}>
              {[
                { t: "T+0ms",    color: "#3b82f6", text: "Your app throws an error. stderr receives the traceback." },
                { t: "T+10ms",   color: "#8b5cf6", text: "Sentinel Agent detects the error pattern in the output stream." },
                { t: "T+50ms",   color: "#06b6d4", text: "CECE Engine captures stack trace, line numbers, environment, system state." },
                { t: "T+80ms",   color: "#10b981", text: "Memory Store checked — is this a known error pattern? (>90% match = instant fix)" },
                { t: "T+200ms",  color: "#f59e0b", text: "If new: context packaged and sent to LLM. AI analyzes root cause." },
                { t: "T+3–15s",  color: "#f97316", text: "LLM returns diagnosis, confidence score, and suggested fix type." },
                { t: "T+15–25s", color: "#ef4444", text: "Fix generated, tested in sandbox. If it fails, Loop Engine tries again (up to 10x)." },
                { t: "T+25–30s", color: "#22c55e", text: "Fix applied to your real project. App restarted. Resolution stored in memory." },
              ].map((row) => (
                <div className={styles.timelineRow} key={row.t}>
                  <span className={styles.timelineTime} style={{ color: row.color }}>{row.t}</span>
                  <div className={styles.timelineDot} style={{ background: row.color }} />
                  <p>{row.text}</p>
                </div>
              ))}
            </div>

            <div className={`${styles.glassCard} ${styles.animCard}`}>
              <h3>The Loop Engine</h3>
              <p>
                If the first fix doesn't work, AutoHeal doesn't give up. The
                Loop Engine tries progressively more sophisticated approaches:
              </p>
              <div className={styles.loopGrid}>
                {[
                  { n: "1", label: "Direct fix", sub: "Most confident patch" },
                  { n: "2", label: "Variant fix", sub: "Second-ranked patch" },
                  { n: "3", label: "Re-diagnose", sub: "Expanded context" },
                  { n: "4", label: "Different approach", sub: "Switch strategy type" },
                  { n: "5+", label: "Deep analysis", sub: "Full dep tree scan" },
                  { n: "Max", label: "Escalate to you", sub: "Full report provided" },
                ].map((item) => (
                  <div className={styles.loopItem} key={item.n}>
                    <span className={styles.loopN}>{item.n}</span>
                    <strong>{item.label}</strong>
                    <small>{item.sub}</small>
                  </div>
                ))}
              </div>
            </div>
          </section>

          {/* ─────────────────── SECTION 5 ─────────────────── */}
          <section id="cli-commands" className={styles.section}>
            <h2>CLI Commands</h2>
            <p className={styles.sectionLead}>
              Every command you can run in your terminal.
            </p>

            {[
              {
                cmd: "autoheal init [path]",
                icon: <Zap size={16} />,
                desc: "Initialize AutoHeal in a project directory. Creates .autoheal/ folder with config.toml and the error memory database.",
                example: "autoheal init\nautoheal init ./my-project",
              },
              {
                cmd: "autoheal run \"<command>\"",
                icon: <Play size={16} />,
                desc: "Run any command with AutoHeal monitoring active. AutoHeal wraps the process and watches for errors.",
                example: `autoheal run "python app.py"\nautoheal run "npm start"\nautoheal run "node server.js"\nautoheal run "go run main.go"`,
              },
              {
                cmd: "autoheal status",
                icon: <Eye size={16} />,
                desc: "View a status report — how many errors were caught, how many were auto-fixed, how many patterns are in memory.",
                example: "autoheal status",
              },
              {
                cmd: "autoheal history [-n 20]",
                icon: <History size={16} />,
                desc: "Show the history of errors and fixes. Use -n to limit how many entries are shown.",
                example: "autoheal history\nautoheal history -n 50",
              },
              {
                cmd: "autoheal config list",
                icon: <Settings size={16} />,
                desc: "Show all current configuration settings in a formatted table.",
                example: "autoheal config list",
              },
              {
                cmd: "autoheal config set <key> <value>",
                icon: <Settings size={16} />,
                desc: "Set any configuration value. Keys use dot notation (section.field).",
                example: `autoheal config set llm.provider google\nautoheal config set llm.api_key YOUR_KEY\nautoheal config set llm.model gemini-2.0-flash`,
              },
              {
                cmd: "autoheal config get <key>",
                icon: <Settings size={16} />,
                desc: "Retrieve a single config value.",
                example: "autoheal config get llm.provider",
              },
              {
                cmd: "autoheal diagnose \"<error>\"",
                icon: <Cpu size={16} />,
                desc: "Manually ask AutoHeal to diagnose an error message without running a process.",
                example: `autoheal diagnose "TypeError: cannot read property of undefined"`,
              },
              {
                cmd: "autoheal version",
                icon: <Info size={16} />,
                desc: "Show the installed version of AutoHeal AI.",
                example: "autoheal version",
              },
            ].map((c) => (
              <div className={`${styles.cmdCard} ${styles.animCard}`} key={c.cmd}>
                <div className={styles.cmdHeader}>
                  <div className={styles.cmdIcon}>{c.icon}</div>
                  <code className={styles.cmdName}>{c.cmd}</code>
                </div>
                <p className={styles.cmdDesc}>{c.desc}</p>
                <CodeBlock label="example">{c.example}</CodeBlock>
              </div>
            ))}
          </section>

          {/* ─────────────────── SECTION 6 ─────────────────── */}
          <section id="configuration" className={styles.section}>
            <h2>Configuration</h2>
            <p className={styles.sectionLead}>
              All settings live in <code>.autoheal/config.toml</code> inside
              your project. You can edit it directly or use{" "}
              <code>autoheal config set</code>.
            </p>

            <CodeBlock label=".autoheal/config.toml">{`[general]
mode = "auto"           # auto | suggest | manual
verbose = false
log_level = "info"      # debug | info | warning | error

[sentinel]
watch_stdout = true     # Monitor standard output
watch_stderr = true     # Monitor standard error
watch_exit_code = true  # Catch non-zero exit codes
health_check_interval = 30

[diagnostics]
timeout = 30            # Max seconds for diagnosis
strategies = ["pattern_match", "llm_reasoning"]

[resolution]
confidence_threshold = 0.75   # Min confidence to auto-fix
code_patch_threshold = 0.90   # Min confidence for code patches
create_backup = true          # Git commit before any code change
max_patch_lines = 50          # Max lines a patch can change

[memory]
enabled = true
max_patterns = 10000   # Max error patterns to store

[llm]
provider = "google"            # openai | anthropic | google | ollama
model = "gemini-2.0-flash"     # Leave empty for auto-select
api_key = "AIzaSy..."          # Your API key (kept local, never sent)
temperature = 0.2              # Low = more deterministic fixes
max_tokens = 4096
timeout = 60

[redaction]
enabled = true          # Strip secrets from LLM payloads
patterns = []           # Add custom regex patterns to redact`}</CodeBlock>

            <div className={styles.configTable}>
              <div className={styles.configRow + " " + styles.configHeader}>
                <span>Key</span><span>Default</span><span>Description</span>
              </div>
              {[
                ["llm.provider", `"openai"`, "AI provider: openai, anthropic, google, ollama"],
                ["llm.model", `""`, "Model name — empty = auto-select best for provider"],
                ["llm.api_key", `""`, "Your API key (stored locally in config.toml)"],
                ["resolution.confidence_threshold", "0.75", "Minimum AI confidence to apply any fix automatically"],
                ["resolution.code_patch_threshold", "0.90", "Minimum confidence to modify source code files"],
                ["resolution.create_backup", "true", "Create a git commit before applying any code patch"],
                ["loop.max_iterations", "10", "How many fix attempts before escalating to you"],
                ["general.mode", `"auto"`, "auto = fix silently, suggest = ask first, manual = detect only"],
              ].map(([k, d, desc]) => (
                <div className={styles.configRow} key={k}>
                  <code>{k}</code><code>{d}</code><span>{desc}</span>
                </div>
              ))}
            </div>
          </section>

          {/* ─────────────────── SECTION 7 ─────────────────── */}
          <section id="llm-providers" className={styles.section}>
            <h2>LLM Providers</h2>
            <p className={styles.sectionLead}>
              AutoHeal works with all major AI providers and also locally with
              Ollama (no internet required).
            </p>

            {[
              {
                name: "Google Gemini",
                badge: "Recommended · Free tier",
                badgeColor: "#22c55e",
                model: "gemini-2.0-flash",
                keyUrl: "https://aistudio.google.com/apikey",
                cmds: `autoheal config set llm.provider google\nautoheal config set llm.model gemini-2.0-flash\nautoheal config set llm.api_key AIzaSy...`,
              },
              {
                name: "OpenAI",
                badge: "Default",
                badgeColor: "#3b82f6",
                model: "gpt-4o",
                keyUrl: "https://platform.openai.com/api-keys",
                cmds: `autoheal config set llm.provider openai\nautoheal config set llm.api_key sk-proj-...`,
              },
              {
                name: "Anthropic Claude",
                badge: "Great for careful analysis",
                badgeColor: "#8b5cf6",
                model: "claude-sonnet-4-...",
                keyUrl: "https://console.anthropic.com",
                cmds: `autoheal config set llm.provider anthropic\nautoheal config set llm.api_key sk-ant-...`,
              },
              {
                name: "Ollama (Local)",
                badge: "No internet · Private",
                badgeColor: "#f59e0b",
                model: "llama3.1 / codellama",
                keyUrl: "https://ollama.com",
                cmds: `# Install Ollama first: https://ollama.com
ollama pull llama3.1

autoheal config set llm.provider ollama
autoheal config set llm.model llama3.1`,
              },
            ].map((p) => (
              <div className={`${styles.providerCard} ${styles.animCard}`} key={p.name}>
                <div className={styles.providerHeader}>
                  <h3>{p.name}</h3>
                  <span className={styles.providerBadge} style={{ borderColor: p.badgeColor, color: p.badgeColor }}>
                    {p.badge}
                  </span>
                </div>
                <p className={styles.providerModel}>Default model: <code>{p.model}</code></p>
                <p className={styles.providerKeyLink}>
                  Get API key: <a href={p.keyUrl} target="_blank" rel="noreferrer" className="hoverable">{p.keyUrl}</a>
                </p>
                <CodeBlock label="setup">{p.cmds}</CodeBlock>
              </div>
            ))}
          </section>

          {/* ─────────────────── SECTION 8 ─────────────────── */}
          <section id="integrating" className={styles.section}>
            <h2>Integrating with Your Projects</h2>
            <p className={styles.sectionLead}>
              AutoHeal works with any project. Here are concrete examples.
            </p>

            {[
              {
                title: "Python Flask / FastAPI / Django",
                steps: [
                  "cd to your Python project folder",
                  "Run: autoheal init",
                  "Set your API key",
                  `Run: autoheal run "python app.py"`,
                ],
                note: "AutoHeal intercepts Python exceptions, ImportErrors, database errors, and more.",
              },
              {
                title: "Node.js / Express / Next.js",
                steps: [
                  "cd to your Node project",
                  "Run: autoheal init",
                  "Set your API key",
                  `Run: autoheal run "npm start" or autoheal run "node server.js"`,
                ],
                note: "AutoHeal watches stderr for JavaScript/TypeScript errors, uncaught exceptions, and module errors.",
              },
              {
                title: "Static Site with Local Server (HTML/CSS/JS)",
                steps: [
                  "cd to your static site folder",
                  "Run: autoheal init",
                  `Run: autoheal run "python -m http.server 8000"`,
                ],
                note: "AutoHeal monitors the server process for any errors that occur while serving files.",
              },
              {
                title: "Any Other Language / Framework",
                steps: [
                  "cd to your project",
                  "Run: autoheal init",
                  `Run: autoheal run "your-normal-start-command"`,
                ],
                note: "AutoHeal works with Go, Rust, Ruby, PHP, Java — anything that runs as a process in your terminal.",
              },
            ].map((ex) => (
              <div className={`${styles.exampleCard} ${styles.animCard}`} key={ex.title}>
                <h3>{ex.title}</h3>
                <ol className={styles.exampleSteps}>
                  {ex.steps.map((s, i) => (
                    <li key={i}>{s}</li>
                  ))}
                </ol>
                <div className={styles.noteBox}>
                  <Info size={14} />
                  <span>{ex.note}</span>
                </div>
              </div>
            ))}

            <div className={`${styles.glassCard} ${styles.animCard}`}>
              <h3>Files AutoHeal creates in your project</h3>
              <p style={{ marginBottom: 16 }}>
                AutoHeal only creates files inside <code>.autoheal/</code>.
                Your project files are never touched during init or monitoring —
                only during a fix (with a git backup first).
              </p>
              <CodeBlock label="your-project/">{`.autoheal/
├── config.toml    ← your settings (provider, model, key, thresholds)
└── autoheal.db    ← error memory + fix history database (SQLite)`}</CodeBlock>
              <p style={{ marginTop: 12 }}>
                The <code>.autoheal/</code> folder is automatically added to
                your <code>.gitignore</code> so it is never committed to git.
              </p>
            </div>
          </section>

          {/* ─────────────────── SECTION 9 ─────────────────── */}
          <section id="faq" className={styles.section}>
            <h2>Frequently Asked Questions</h2>

            {[
              {
                q: "Does AutoHeal change my project code without asking?",
                a: "Only if the AI confidence is above 0.90 (configurable). Below that threshold it tells you what it found and suggests a fix but waits for you. You can set mode = 'suggest' to always ask first, or 'manual' to detect only.",
              },
              {
                q: "What happens if the fix makes things worse?",
                a: "AutoHeal tests every fix in a sandboxed subprocess before applying it. It also creates a git commit as a restore point before modifying any file. If something goes wrong, you can always git revert to get back to where you were.",
              },
              {
                q: "I set llm.provider to google but it still uses OpenAI. Why?",
                a: "You must run autoheal config set commands from inside the project folder where you ran autoheal init. Each project has its own .autoheal/config.toml — run the commands with cd to your project first, then set the provider.",
              },
              {
                q: "Does my code get sent to the AI provider?",
                a: "Only the relevant error context — stack trace, a small snippet of the failing code, and environment info. Secrets and API keys are automatically redacted before anything leaves your machine. You can also use Ollama for fully local, offline operation.",
              },
              {
                q: "Can I use AutoHeal on a production server?",
                a: "Yes. Run autoheal run 'your-start-command' on the server the same way you would locally. Set confidence thresholds higher for production to be safe, and consider mode = 'suggest' so fixes require human approval before applying.",
              },
              {
                q: "What if AutoHeal itself crashes?",
                a: "AutoHeal is designed to never crash your host application. If AutoHeal itself encounters an unhandled error, it exits cleanly without affecting your running process. Your app continues normally.",
              },
            ].map((faq, i) => (
              <details className={`${styles.faqItem} ${styles.animCard}`} key={i}>
                <summary className={styles.faqQ}>{faq.q}</summary>
                <p className={styles.faqA}>{faq.a}</p>
              </details>
            ))}
          </section>

        </article>
      </div>

      <Footer />
    </main>
  );
}
