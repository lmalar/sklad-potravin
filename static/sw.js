self.addEventListener('install', (e) => {
    console.log('PWA Sklad nainstalován');
});
self.addEventListener('fetch', (e) => {
    // Necháváme prázdné, chceme jen splnit PWA standard
});