openerp.bestja_stores = function(instance) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    instance.bestja_stores.WidgetNonDisableableButton = instance.web.form.WidgetButton.extend({
        check_disable: function() {
            console.log('huhhh');
            this.$el.prop('disabled', this.force_disabled);
            this.$el.css('color', this.force_disabled ? 'grey' : '');
        }
    });

    instance.web.form.custom_widgets.add('non_disableable_button', 'instance.bestja_stores.WidgetNonDisableableButton');
}
