import {
  useState,
} from "react";

import ChatPage from "./pages/ChatPage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";

import {
  AuthProvider,
  useAuth,
} from "./context/AuthContext";


function AppContent() {
  const {
    user,
    loading,
  } = useAuth();

  const [
    authPage,
    setAuthPage,
  ] = useState("login");


  if (loading) {
    return (
      <div className="auth-page">
        <div className="auth-loading">
          Loading...
        </div>
      </div>
    );
  }


  if (!user) {
    if (
      authPage === "register"
    ) {
      return (
        <RegisterPage
          onShowLogin={() =>
            setAuthPage(
              "login"
            )
          }
        />
      );
    }


    return (
      <LoginPage
        onShowRegister={() =>
          setAuthPage(
            "register"
          )
        }
      />
    );
  }


  return <ChatPage />;
}


export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}