'use client';

import { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import Notification, { NotificationProps, NotificationType } from './Notification';

interface NotificationContextType {
  showNotification: (
    type: NotificationType,
    title: string,
    message: string,
    xp?: number
  ) => void;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

export function useNotifications() {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within NotificationProvider');
  }
  return context;
}

interface NotificationProviderProps {
  children: ReactNode;
}

export function NotificationProvider({ children }: NotificationProviderProps) {
  const [notifications, setNotifications] = useState<Omit<NotificationProps, 'onClose'>[]>([]);

  const showNotification = useCallback(
    (type: NotificationType, title: string, message: string, xp?: number) => {
      const id = Math.random().toString(36).substr(2, 9);
      setNotifications((prev) => [...prev, { id, type, title, message, xp }]);
    },
    []
  );

  const closeNotification = useCallback((id: string) => {
    setNotifications((prev) => prev.filter((notif) => notif.id !== id));
  }, []);

  return (
    <NotificationContext.Provider value={{ showNotification }}>
      {children}
      <div className="fixed top-4 right-4 z-50 flex flex-col items-end">
        {notifications.map((notif) => (
          <Notification key={notif.id} {...notif} onClose={closeNotification} />
        ))}
      </div>
    </NotificationContext.Provider>
  );
}
