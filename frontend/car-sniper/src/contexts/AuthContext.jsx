import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [isAuthOpen, setIsAuthOpen] = useState(false);

  useEffect(() => {
    const storedEmail = localStorage.getItem('user_email');
    const storedRole = localStorage.getItem('user_role');
    if (storedEmail) {
      setCurrentUser({ email: storedEmail, role: storedRole || 'user' });
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('jwt_token');
    localStorage.removeItem('user_email');
    localStorage.removeItem('user_role');
    setCurrentUser(null);
  };

  const login = (email, token, role) => {
    localStorage.setItem('jwt_token', token);
    localStorage.setItem('user_email', email);
    localStorage.setItem('user_role', role);
    setCurrentUser({ email, role });
  };

  return (
    <AuthContext.Provider
      value={{
        currentUser,
        setCurrentUser,
        isAuthOpen,
        setIsAuthOpen,
        handleLogout,
        login
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
