const CACHE_NAME = 'whisper-stt-v1';
const urlsToCache = [
    '/',
    '/static/index.html',
    '/static/service-worker.js',
    '/static/asr.png'
];

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(urlsToCache))
    );
});

self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => response || fetch(event.request))
    );
});