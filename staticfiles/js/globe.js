// globe.js

let scene, camera, renderer, globe, tooltip, loadingContainer;

init();
animate();

function init() {
    const container = document.getElementById('globe-container');
    tooltip = document.getElementById('tooltip');
    loadingContainer = document.getElementById('loading-container');

    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
    camera.position.set(0, 0, 50);

    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    container.appendChild(renderer.domElement);

    const geometry = new THREE.SphereGeometry(15, 64, 64);
    const material = new THREE.MeshPhongMaterial({
        map: new THREE.TextureLoader().load('path/to/earth_texture.jpg'),
        bumpMap: new THREE.TextureLoader().load('path/to/earth_bump.jpg'),
        bumpScale: 0.5,
    });

    globe = new THREE.Mesh(geometry, material);
    scene.add(globe);

    const ambientLight = new THREE.AmbientLight(0xcccccc);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.6);
    directionalLight.position.set(5, 3, 5);
    scene.add(directionalLight);

    window.addEventListener('resize', onWindowResize);
}

function animate() {
    requestAnimationFrame(animate);
    globe.rotation.y += 0.002;
    render();
}

function render() {
    renderer.render(scene, camera);
}

function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}
