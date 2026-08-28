import { useState } from "react";

import {
  useAuth,
} from "../context/AuthContext";


export default function LoginPage({
  onShowRegister,
}) {
  const { login } = useAuth();

  const [email, setEmail] =
    useState("");

  const [password, setPassword] =
    useState("");

  const [error, setError] =
    useState("");

  const [loading, setLoading] =
    useState(false);


  const handleSubmit =
    async (event) => {
      event.preventDefault();

      if (
        !email.trim() ||
        !password
      ) {
        setError(
          "Please enter your email and password."
        );

        return;
      }

      setError("");
      setLoading(true);

      try {
        await login({
          email: email.trim(),
          password,
        });

      } catch (error) {
        console.error(
          "Login failed:",
          error
        );

        const message =
          error.response?.data?.detail ||
          "Invalid email or password.";

        setError(
          typeof message === "string"
            ? message
            : "Login failed."
        );

      } finally {
        setLoading(false);
      }
    };


  return (
    <div className="auth-page">

      <div className="auth-card">

        {/* ORANGE CHATBOT LOGO */}

        <div className="auth-chatbot-logo">
          <svg
            viewBox="0 0 24 24"
            width="30"
            height="30"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.8"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M12 3l1.2 3.5L17 8l-3.8 1.5L12 13l-1.3-3.5L7 8l3.7-1.5L12 3z" />

            <path d="M18.5 12.5l.7 2 2.1.7-2.1.8-.7 2-.8-2-2-.8 2-.7.8-2z" />

            <path d="M5.5 14.5l.6 1.6 1.6.6-1.6.6-.6 1.7-.6-1.7-1.7-.6 1.7-.6.6-1.6z" />
          </svg>
        </div>


        {/* TITLE */}

        <div className="auth-brand">

          <h1>
            Welcome back
          </h1>

          <p>
            Sign in to continue your
            conversations.
          </p>

        </div>


        {/* LOGIN FORM */}

        <form
          className="auth-form"
          onSubmit={handleSubmit}
        >

          <label>
            Email

            <input
              type="email"
              value={email}
              onChange={(event) =>
                setEmail(
                  event.target.value
                )
              }
              placeholder="you@example.com"
              autoComplete="email"
            />
          </label>


          <label>
            Password

            <input
              type="password"
              value={password}
              onChange={(event) =>
                setPassword(
                  event.target.value
                )
              }
              placeholder="Enter your password"
              autoComplete="current-password"
            />
          </label>


          {error && (
            <div className="auth-error">
              {error}
            </div>
          )}


          <button
            type="submit"
            className="auth-primary-button"
            disabled={loading}
          >
            {loading
              ? "Signing in..."
              : "Sign in"}
          </button>

        </form>


        {/* CREATE ACCOUNT */}

        <p className="auth-switch">

          Don't have an account?

          <button
            type="button"
            onClick={
              onShowRegister
            }
          >
            Create account
          </button>

        </p>

      </div>

    </div>
  );
}