"use strict";

let app = {};

app.data = {
    data: function() {
        return {
            checklists: [],
            drawn_coordinates: drawn_coordinates || []
        };
    },
    methods: {
        loadChecklists: function() {
            let self = this;
            axios.get(load_checklists_url).then(response => {
                self.checklists = response.data.checklists;
            }).catch(error => {
                console.error('Error loading checklists:', error);
            });
        },
        deleteChecklist: function(checklist_id) {
            let self = this;
            if (confirm("Are you sure you want to delete this checklist?")) {
                axios.delete(delete_checklist_url + '/' + checklist_id).then(response => {
                    self.checklists = self.checklists.filter(checklist => checklist.id !== checklist_id);
                }).catch(error => {
                    console.error('Error deleting checklist:', error);
                });
            }
        },
        updateField: function(checklist_id, field, newValue) {
            let payload = {
                checklist_id: checklist_id,
                field: field,
                value: newValue
            };
            axios.post(update_checklist_url, payload).then(response => {
                console.log('Field updated successfully');
            }).catch(error => {
                console.error('Error updating field:', error);
            });
        }
    },
    mounted() {
        this.loadChecklists();
        console.log(drawn_coordinates);
    }
};

app.vue = Vue.createApp(app.data).mount("#app");