odoo.define('flc_help_center.kanban', function (require) {
    "use strict";

    var KanbanController = require('web.KanbanController');
    var KanbanView = require('web.KanbanView');
    var viewRegistry = require('web.view_registry');

    var HelpCenterKanbanController = KanbanController.extend({
        events: _.extend({}, KanbanController.prototype.events, {
            'click .oe_kanban_image': '_onImageClick',
        }),

        _onImageClick: function (ev) {
            ev.stopPropagation();
            var $target = $(ev.currentTarget);
            var resourceId = $target.data('resource-id');
            var resourceType = $target.data('type');

            // Handle different resource types
            if (resourceType === 'screenshot') {
                // Open image or PDF
                this._rpc({
                    model: 'help.center.app',
                    method: 'get_resource_url',
                    args: [resourceId],
                }).then(function (result) {
                    if (result) {
                        window.open(result, '_blank');
                    }
                });
            } else if (resourceType === 'video') {
                // Open video
                this._rpc({
                    model: 'help.center.app',
                    method: 'get_video_url',
                    args: [resourceId],
                }).then(function (result) {
                    if (result) {
                        window.open(result, '_blank');
                    }
                });
            } else if (resourceType === 'faq') {
                // Open FAQ form
                this.do_action({
                    type: 'ir.actions.act_window',
                    res_model: 'help.center.faq',
                    res_id: resourceId,
                    views: [[false, 'form']],
                    target: 'new',
                });
            }
        },
    });

    var HelpCenterKanbanView = KanbanView.extend({
        config: _.extend({}, KanbanView.prototype.config, {
            Controller: HelpCenterKanbanController,
        }),
    });

    viewRegistry.add('help_center_kanban', HelpCenterKanbanView);

    return HelpCenterKanbanView;
});

