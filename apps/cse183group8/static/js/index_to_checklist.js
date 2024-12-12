"use strict";

// Utility function to access raw values
function toRaw(obj) {
    return obj.__v_raw || obj;
}

// Vue Application
const app = Vue.createApp({
    data() {
        return {
            drawn_coordinates: drawn_coordinates || [],
            latitude: '',
            longitude: ''
        };
    },
    computed: {
        latUpdate() {
            return this.latitude;
        },
        longUpdate() {
            return this.longitude;
        }
    },
    methods: {

    },
    mounted() {
        console.log("drawn_coordinates:", this.drawn_coordinates);
        if (this.drawn_coordinates.length > 0) {
            const { lat, lng } = this.drawn_coordinates[0];
            this.latitude = lat.toFixed(6); // Update latitude
            this.longitude = lng.toFixed(6); // Update longitude
        }
    }
});

// Mount the Vue app to the DOM
const vueInstance = app.mount("#app");

// Functionality for additional data loading
function loadData() {
    console.log("Loading additional data...");
    // Implement data loading logic here
}

// Initialize data loading
loadData();