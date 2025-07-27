importScripts('https://www.gstatic.com/firebasejs/10.12.2/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.12.2/firebase-messaging-compat.js');

firebase.initializeApp({
  apiKey: "AIzaSyAdqAoT2IewbCknzqqMQ5En5lUIYWJv0e4",
  authDomain: "storagefinsight.firebaseapp.com",
  projectId: "storagefinsight",
  messagingSenderId: "822642518224",
  appId: "1:822642518224:web:7d03616bb2dcd6dc04d6d5"
});

const messaging = firebase.messaging();

messaging.onBackgroundMessage(function(payload) {
  console.log('[firebase-messaging-sw.js] Received background message ', payload);
  const notificationTitle = payload.notification.title;
  const notificationOptions = {
    body: payload.notification.body,
    icon: '/placeholder.svg'
  };

  self.registration.showNotification(notificationTitle, notificationOptions);
});