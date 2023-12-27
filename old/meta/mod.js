var mutuallyExclusiveComponents = ["wakfu.mod.chat"];

function Component()
{
	component.valueChanged.connect(this, Component.prototype.valueChanged);
    var modname = component.name.substring(component.name.lastIndexOf('.') + 1);
    component.registerPathForUninstallation("@WAKFU_MODS@/" + modname, true);
}

Component.prototype.valueChanged = function (key, value)
{
    var page = gui.currentPageWidget();
    if (page != null && page == gui.pageById(QInstaller.ComponentSelection)) {
        if (key == "UncompressedSizeSum" && value > 0) {
            for (var i = 0; i < mutuallyExclusiveComponents.length; i++) {
                page.deselectComponent(mutuallyExclusiveComponents[i]);
            }
        }
    }
}

Component.prototype.createOperations = function()
{
    component.createOperations();
};

Component.prototype.createOperationsForArchive = function(archive)
{
    component.addOperation("Extract", archive, "@WAKFU_MODS@");
};
