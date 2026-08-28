import {
  createContext,
  useContext,
  useEffect,
  useState,
} from "react";

import {
  clearAccessToken,
  getAccessToken,
  getCurrentUser,
  loginUser,
  logoutUser,
  registerUser,
  setAccessToken,
} from "../services/api";


export const AuthContext =
  createContext(null);


export function AuthProvider({
  children,
}) {
  const [
    user,
    setUser,
  ] = useState(null);

  const [
    loading,
    setLoading,
  ] = useState(true);


  /* =========================================
     CHECK SAVED LOGIN
  ========================================= */

  useEffect(() => {
    const restoreLogin =
      async () => {
        const token =
          getAccessToken();

        if (!token) {
          setLoading(false);
          return;
        }

        try {
          const currentUser =
            await getCurrentUser();

          setUser(
            currentUser
          );

        } catch (error) {
          console.error(
            "Session restore failed:",
            error
          );

          clearAccessToken();

          setUser(null);

        } finally {
          setLoading(false);
        }
      };

    restoreLogin();
  }, []);


  /* =========================================
     LOGIN
  ========================================= */

  const login =
    async ({
      email,
      password,
    }) => {
      const data =
        await loginUser({
          email,
          password,
        });

      setAccessToken(
        data.access_token
      );

      setUser(
        data.user
      );

      return data.user;
    };


  /* =========================================
     REGISTER
  ========================================= */

  const register =
    async ({
      name,
      email,
      password,
    }) => {
      const data =
        await registerUser({
          name,
          email,
          password,
        });

      setAccessToken(
        data.access_token
      );

      setUser(
        data.user
      );

      return data.user;
    };


  /* =========================================
     LOGOUT
  ========================================= */

  const logout =
    async () => {
      try {
        if (getAccessToken()) {
          await logoutUser();
        }

      } catch (error) {
        console.error(
          "Logout API error:",
          error
        );

      } finally {
        clearAccessToken();

        setUser(null);
      }
    };


  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}


export function useAuth() {
  return useContext(
    AuthContext
  );
}