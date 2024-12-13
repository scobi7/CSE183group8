"use strict";

const app = {
    state: {
        data() {
            return {
                checklist_data: [],
                search: [],
                bird_search: localStorage.getItem('bird_search') || '',
                search_active: false,
            };
        },
        
        methods: {
            toggle_search() {
                const trimmedSearch = this.bird_search.trim().toLowerCase();
                
                if (trimmedSearch !== '') {
                    this.search_active = true;
                    this.search = this.checklist_data.filter(entry => 
                        entry.common_name.toLowerCase().startsWith(trimmedSearch)
                    );
                } else {
                    this.search_active = false;
                    this.search = [];
                }
                
                localStorage.setItem('bird_search', this.bird_search);
            },
            
            async updateSightings(species, new_sightings) {
                try {
                    const response = await axios.post(update_sightings_url, {
                        common_name: species.common_name,
                        new_sightings: new_sightings
                    });
                    
                    species.total_sightings = response.data.total_sightings;
                    location.reload();
                } catch (error) {
                    console.error('Error updating the sightings:', error);
                }
            },
            
            handleKeyUp(event, species) {
                if (event.key === 'Enter') {
                    this.updateSightings(species, species.new_sightings);
                }
            },
            
            async incrementSightings(species) {
                const new_sightings = (species.new_sightings || 0) + 1;
                
                try {
                    const response = await axios.post(update_sightings_url, {
                        common_name: species.common_name,
                        new_sightings: new_sightings
                    });
                    
                    species.total_sightings = response.data.total_sightings;
                    species.new_sightings = new_sightings;
                    location.reload();
                } catch (error) {
                    console.error('Error incrementing sightings:', error);
                }
            },
        },
        
        mounted() {
            if (this.bird_search.trim() !== '') {
                this.toggle_search();
            }
        }
    },
    
    async loadData() {
        try {
            const response = await axios.get(checklist_data_url);
            
            this.vue.checklist_data = response.data.checklist_data.map(species => ({
                common_name: species.common_name,
                total_sightings: species.total_sightings || 0,
                new_sightings: 0
            }));
            
            if (this.vue.bird_search.trim() !== '') {
                this.vue.toggle_search();
            }
        } catch (error) {
            console.error('Error fetching the checklist data:', error);
        }
    },
    
    init() {
        this.vue = Vue.createApp(this.state).mount("#app");
        this.loadData();
    }
};

// Initialize the application
app.init();