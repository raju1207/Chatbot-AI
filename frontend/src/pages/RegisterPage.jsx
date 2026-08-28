import {
  useState,
} from "react";

import {
  useAuth,
} from "../context/AuthContext";


export default function RegisterPage({
  onShowLogin,
}) {
  const {
    register,
  } = useAuth();

  const [
    name,
    setName,
  ] = useState("");

  const [
    email,
    setEmail,
  ] = useState("");

  const [
    password,
    setPassword,
  ] = useState("");

  const [
    confirmPassword,
    setConfirmPassword,
  ] = useState("");

  const [
    error,
    setError,
  ] = useState("");

  const [
    loading,
    setLoading,
  ] = useState(false);


  const handleSubmit =
    async (event) => {
      event.preventDefault();

      if (
        !name.trim() ||
        !email.trim() ||
        !password
      ) {
        setError(
          "Please complete all fields."
        );

        return;
      }


      if (
        password.length < 8
      ) {
        setError(
          "Password must contain at least 8 characters."
        );

        return;
      }


      if (
        password !==
        confirmPassword
      ) {
        setError(
          "Passwords do not match."
        );

        return;
      }


      setError("");
      setLoading(true);

      try {
        await register({
          name:
            name.trim(),

          email:
            email.trim(),

          password,
        });

      } catch (error) {
        console.error(
          "Registration failed:",
          error
        );

        const message =
          error.response?.data?.detail ||
          "Registration failed.";

        setError(
          typeof message === "string"
            ? message
            : "Registration failed."
        );

      } finally {
        setLoading(false);
      }
    };


  return (
    <div className="auth-page">
      <div className="auth-card">

        <div className="auth-brand">
          <div className="auth-logo">
            AI
          </div>

          <h1>
            Create account
          </h1>

          <p>
            Start your private AI
            conversations.
          </p>
        </div>


        <form
          className="auth-form"

          onSubmit={
            handleSubmit
          }
        >
          <label>
            Name

            <input
              type="text"

              value={name}

              onChange={(event) =>
                setName(
                  event.target.value
                )
              }

              placeholder=
                "Your name"

              autoComplete="name"
            />
          </label>


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

              placeholder=
                "you@example.com"

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

              placeholder=
                "Minimum 8 characters"

              autoComplete=
                "new-password"
            />
          </label>


          <label>
            Confirm password

            <input
              type="password"

              value={
                confirmPassword
              }

              onChange={(event) =>
                setConfirmPassword(
                  event.target.value
                )
              }

              placeholder=
                "Enter password again"

              autoComplete=
                "new-password"
            />
          </label>


          {error && (
            <div
              className=
                "auth-error"
            >
              {error}
            </div>
          )}


          <button
            type="submit"

            className=
              "auth-primary-button"

            disabled={loading}
          >
            {loading
              ? "Creating account..."
              : "Create account"}
          </button>
        </form>


        <p className="auth-switch">
          Already have an account?

          <button
            type="button"

            onClick={
              onShowLogin
            }
          >
            Sign in
          </button>
        </p>

      </div>
    </div>
  );
}