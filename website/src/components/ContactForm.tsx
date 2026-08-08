"use client";

import { useState } from "react";
import styles from "./ContactForm.module.css";
import { Send, CheckCircle2 } from "lucide-react";

export default function ContactForm() {
  const [status, setStatus] = useState<"idle" | "submitting" | "success" | "error">("idle");

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setStatus("submitting");

    const formData = new FormData(e.currentTarget);
    // Replace with the user's actual Web3Forms Access Key
    formData.append("access_key", "YOUR_WEB3FORMS_ACCESS_KEY_HERE");

    try {
      const res = await fetch("https://api.web3forms.com/submit", {
        method: "POST",
        body: formData
      });
      const data = await res.json();
      
      if (data.success) {
        setStatus("success");
      } else {
        setStatus("error");
      }
    } catch (err) {
      setStatus("error");
    }
  };

  return (
    <section id="contact" className={`section ${styles.contactSection}`}>
      <div className={`container ${styles.container}`}>
        <div className={styles.header}>
          <h2 className="h2">Let's talk</h2>
          <p className="p-large">
            Have feedback, feature requests, or want to contribute? Send a message directly to the maintainer.
          </p>
        </div>

        {status === "success" ? (
          <div className={styles.successMessage}>
            <CheckCircle2 size={48} color="var(--accent)" />
            <h3>Message Sent!</h3>
            <p>Thank you for reaching out. We'll get back to you soon.</p>
          </div>
        ) : (
          <form className={styles.form} onSubmit={handleSubmit}>
            <div className={styles.inputGroup}>
              <div className={styles.field}>
                <label htmlFor="name">Name</label>
                <input type="text" id="name" name="name" required className="hoverable" />
              </div>
              <div className={styles.field}>
                <label htmlFor="email">Email</label>
                <input type="email" id="email" name="email" required className="hoverable" />
              </div>
            </div>
            
            <div className={styles.field}>
              <label htmlFor="message">Message</label>
              <textarea id="message" name="message" rows={5} required className="hoverable"></textarea>
            </div>

            {status === "error" && (
              <p className={styles.errorMsg}>Something went wrong. Please try again later.</p>
            )}

            <button 
              type="submit" 
              className={`btn-primary hoverable ${styles.submitBtn}`}
              disabled={status === "submitting"}
            >
              {status === "submitting" ? "Sending..." : (
                <>
                  <Send size={18} />
                  Send Message
                </>
              )}
            </button>
          </form>
        )}
      </div>
    </section>
  );
}
