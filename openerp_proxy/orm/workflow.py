from openerp_proxy.orm.record import RecordBase
from openerp_proxy.orm.record import ObjectRecords
from openerp_proxy.exceptions import ObjectException


__all__ = ('RecordWorkflow', 'ObjectWorkflow')


class ObjectWorkflow(ObjectRecords):
    def __init__(self, erp_proxy, object_name):
        super(ObjectWorkflow, self).__init__(erp_proxy, object_name)
        self._workflow = None

    @property
    def workflow(self):
        """ Returns Record instance of "workflow" object
            related to this Object

            If there are no workflow for an object then False will be returned
        """
        if self._workflow is None:
            wkf_obj = self.proxy.get_obj('workflow')
            # TODO: implement correct behavior for situations with few
            # workflows for same model.
            wkf_records = wkf_obj.search_records([('osv', '=', self.name)])
            if wkf_records and len(wkf_records) > 1:
                raise ObjectException("More then one workflow per model not supported "
                                      "be current version of openerp_proxy!")
            self._workflow = wkf_records and wkf_records[0] or False
        return self._workflow

    def workflow_trg(self, obj_id, signal):
        """ Triggers specified signal for object's workflow
        """
        assert isinstance(obj_id, (int, long)), "obj_id must be integer"
        assert isinstance(signal, basestring), "signal must be string"
        return self.proxy.execute_wkf(self.name, signal, obj_id)


class RecordWorkflow(RecordBase):
    """ Adds ability to browse related fields from record
    """

    def __init__(self, obj, data):
        super(RecordWorkflow, self).__init__(obj, data)
        self._workflow_instance = None

    @property
    def workflow_instance(self):
        """ Retunrs workflow instance related to this record
        """
        if self._workflow_instance is None:
            wkf = self._object.workflow
            if not wkf:
                self._workflow_instance = False
            else:
                wkf_inst_obj = self._proxy.get_obj('workflow.instance')
                wkf_inst_records = wkf_inst_obj.search_records([('wkf_id', '=', wkf.id),
                                                                ('res_id', '=', self.id)], limit=1)
                self._workflow_instance = wkf_inst_records and wkf_inst_records[0] or False
        return self._workflow_instance

    @property
    def workflow_items(self):
        """ Returns list of related workflow.woritem objects
        """
        # TODO: think about adding caching
        workitem_obj = self._proxy.get_obj('workflow.workitem')
        wkf_inst = self.workflow_instance
        if wkf_inst:
            return workitem_obj.search_records([('inst_id', '=', wkf_inst.id)])
        return []

    def workflow_trg(self, signal):
        """ trigger's specified signal on record's related workflow
        """
        return self._object.workflow_trg(self.id, signal)

    def refresh(self):
        """Cleanup record caches and reread data
        """
        super(RecordWorkflow, self).refresh()
        self._workflow_instance = None
        return self