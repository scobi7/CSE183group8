"use strict";

let app = {};


app.data = {    
    data: function() {
        return {
            chart: undefined,

            chart_data: [12, 19, 3, 5, 2, 3], //TODO change based on species selected
            chart_labels: ['day 1?', 'day 2', 'day 3', 'day 4', 'day 5', 'day 6'], //change

            bird_list: [{species: "White-crowned Sparrow", "day": "2024-01-02", count: 10}, {species: "Song Sparrow", "day": "2024-01-02", count: 10}, {species: "American Crow", "day": "2024-01-02", count: 10}, {species: "American Crow", "day": "2024-01-02", count: 10}, {species: "American Crow", "day": "2024-01-02", count: 10}, {species: "American Crow", "day": "2024-01-02", count: 10}, {species: "American Crow", "day": "2024-01-02", count: 10}],  //dummy variables for testing
            top_contributors: [{name: "guy", contributions: 5}, {name: "person", contributions: 2}], //not final structure

            sightings: [],
            checklist: [],

            total_sightings: 0,
            total_checklists: 0,

            //selected region coordinates
            x1: 0,
            y1: 0,

            x2: 0,
            y2: 0,

            dropdown_active: false, // dropdown to appear or not
            active_species: null, // true/false for selected bird in dropdown
        };
    },
    methods: {        

        get_sightings: function() {
            let self = this;
            axios.post(get_location_data_url, {

            }).then(function (r) {
                //self.sightings = r.data.sightings;
                //self.checklist = r.data.checklist;
                //somehow get region coordinates
            });
        },

        /********************
         * Draws a graph using chart.js depending on which bird is selected by user.
         * horizontal axis shows days the bird is spotted
         * vertical axis shows number of times bird is spotted
         ********************/
        make_chart: function() {
            //destory graph if it already exists so we can reuse the canvas
            if (this.chart != undefined) {
                this.chart.destroy();
            }
            const ctx = this.$refs.speciesChart; //context
            this.chart = new Chart(ctx, {
                type: 'bar',
                data: {
                labels: this.chart_labels,
                datasets: [{
                    label: '# of Times Seen',  //TODO maybe change label can be a variable for species name + number of times seen
                    data: this.chart_data,
                    borderWidth: 1
                    }]
                },
                options: {
                    scales: {
                        y: {
                        beginAtZero: true
                        }
                    },
                    animation: {
                        duration: 0      // no animation
                    }
                }
            });

        },

        /********************
         * opens or closes the dropdown menu for species selection on click
         ********************/
        click_dropdown: function() {
            this.dropdown_active = !this.dropdown_active;
        },

        /********************
         * closes the dropdown menu for species selection and
         * calls make_graph. Passes which bird is selected
         ********************/
        select_bird: function(bird) {
            this.dropdown_active = false;
            this.active_species = bird.species;


            let self = this;
            axios.post(get_location_data_url, {
            }).then(function (r) {
                self.bird_list=r.data.location_data;
            });

            this.chart_data 

            this.make_chart(); //need to pass in chart_data and chart_labels but with bird specific data
        },




        //temp function
        test_button: function() {
            this.chart_data =  [1, 2, 3, 5, 2, 3];
        },

        //temp function
        test_button2: function() {
            let self = this;
            axios.post(get_location_data_url, {

            }).then(function (r) {
                self.bird_list=r.data.location_data;
            });
        },
    }

    
};

app.vue = Vue.createApp(app.data).mount("#app");

app.load_data = function () {
    axios.get(get_location_data_url).then(function (r) {
        app.vue.chart_data = r.data.location_data["count"];
        app.vue.chart_labels = r.data.location_data["day"];
        app.vue.top_contributors = r.data.contributor_list;
        app.vue.total_sightings = r.data.total_sightings;
        app.vue.total_checklists = r.data.total_checklists;
    });


}

app.load_data();

