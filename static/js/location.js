"use strict";

let app = {};


app.data = {    
    data: function() {
        return {
            chart: undefined,
            chart_data: [12, 19, 3, 5, 2, 3], //TODO change based on species selected
            chart_labels: ['day 1?', 'day 2', 'day 3', 'day 4', 'day 5', 'day 6'], //change

            bird_list: [{species: "bluejay", count: 10}, {species: "sparrow", count: 20}],  //not final structure
            top_contributors: [{name: "guy", contributions: 5}, {name: "person", contributions: 2}], //not final structure

            total_sightings: 0,
            total_checklists: 0,

            //selected region coordinates
            x1: 0,
            y1: 0,

            x2: 0,
            y2: 0,

            dropdown_active: false,
            active_species: null,
        };
    },
    methods: {        

        // TODO need the coordinates of the user's selected region

        // TODO need to fetch the list of Species in the Selected Region
        // TODO need to fetch the total number of sightings in Selected Region

        // TODO need to fetch some information on top contributors for the Selected Region. (maybe total # of contributions)


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
                        duration: 240
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

            //TODO switch the selected bird and update graph
            //bird = {species: "name", count: number, }

            this.make_chart(); //need to pass in chart_data and chart_labels but with bird specific data
        },




        //temp function
        test_button: function() {
            this.chart_data =  [1, 2, 3, 5, 2, 3];
        },

        //temp function
        test_button2: function() {
            
        },
    }

    
};

app.vue = Vue.createApp(app.data).mount("#app");

app.load_data = function () {
    //axios.get(my_callback_url).then(function (r) {
    //    app.vue.my_value = r.data.my_value;

    //TODO Load user selected coordinates

    //TODO Load species

    //TODO Load checklists

    //});


}

app.load_data();

