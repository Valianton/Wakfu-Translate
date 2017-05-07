function Component()
{
    var modname = component.name.substring(component.name.lastIndexOf('.') + 1);
    component.registerPathForUninstallation("@WAKFU_MODS@/" + modname, true);
}

Component.prototype.createOperations = function()
{
    component.createOperations();
};

Component.prototype.createOperationsForArchive = function(archive)
{
    component.addOperation("Extract", archive, "@WAKFU_MODS@");
};
