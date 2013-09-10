(function () {
    if (typeof window.cerebro === "undefined") {
        window.cerebro = {};
    }

    var cerebro = window.cerebro;

    function NeuronClient(url) {
        var self = this;

        this.loaded = {};
        this.ready = false;

        this.sock = new SockJS(url);
        this.sock.onopen = function (e) {
            self.ready = true;
            if (self.onready) self.onready();
        };

        this.sock.onmessage = function (e) {
            var payload = JSON.parse(e.data);
            NeuronClient.opHandlers[payload[0]].apply(self, payload.slice(1));
        };
        this.sock.onclose = function () {
            self.ready = false;
            console.log("lost connection to neuron.");
            if (self.onclose) self.onclose();
        };
    }

    var OPS = NeuronClient.OPS = {
        ERROR: 0,
        LOAD: 1,
        OPERATION: 2,
        ACK: 3,
        CURSOR: 4,
        LEFT: 5,
        JOIN: 6
    };

    NeuronClient.opHandlers = {};

    NeuronClient.serializeCursor = function (cursor) {
        return cursor ? cursor.position + "," + cursor.selectionEnd
                      : null
                      ;
    };

    NeuronClient.prototype = {
        constructor: NeuronClient,

        loadDocument: function (docId, cm) {
            this.sock.send(JSON.stringify([OPS.LOAD, docId]));
            this.loaded[docId] = {
                cm: cm,
                client: null,
                cb: null
            };
        },

        unloadDocument: function (docId) {
            this.sock.send(JSON.stringify([OPS.LEFT, docId]));
            delete this.loaded[docId];
        },

        processRawCursor: function (docId, connId, rawCursor) {
            var cursor = null;

            if (rawCursor !== null) {
                cursor = rawCursor.split(",");
                cursor = {
                    position: parseInt(cursor[0], 10),
                    selectionEnd: parseInt(cursor[1], 10)
                };
            }
            this.loaded[docId].cb.cursor(connId, cursor);
        }
    };

    NeuronClient.opHandlers[OPS.ERROR] = function (msg) {
        console.error("neuron error!", msg);
        if (self.onerror) self.onerror(msg);
    };

    NeuronClient.opHandlers[OPS.LOAD] = function (docId, docRev, clients, content) {
        var self = this;
        var loaded = this.loaded[docId];

        loaded.cm.setValue(content);

        var sockAdapter = {
            sendOperation: function (docRev, op, cursor) {
                self.sock.send(JSON.stringify([OPS.OPERATION, docId, docRev, JSON.stringify(op), NeuronClient.serializeCursor(cursor)]));
            },

            sendCursor: function (cursor) {
                self.sock.send(JSON.stringify([OPS.CURSOR, docId, NeuronClient.serializeCursor(cursor)]));
            },

            registerCallbacks: function (cb) {
                loaded.cb = cb;
            }
        };

        loaded.client = new ot.EditorClient(
            docRev + 1,
            clients,
            sockAdapter,
            new ot.CodeMirrorAdapter(cm)
        );
    };

    NeuronClient.opHandlers[OPS.OPERATION] = function (docId, connId, rawOp, rawCursor) {
        this.loaded[docId].cb.operation(JSON.parse(rawOp));
        this.processRawCursor(docId, connId, rawCursor);
    };

    NeuronClient.opHandlers[OPS.ACK] = function (docId) {
        this.loaded[docId].cb.ack();
    };

    NeuronClient.opHandlers[OPS.CURSOR] = function (docId, connId, rawCursor) {
        this.processRawCursor(docId, connId, rawCursor);
    };

    NeuronClient.opHandlers[OPS.LEFT] = function (docId, connId) {
        this.loaded[docId].cb.client_left(connId);
    };

    NeuronClient.opHandlers[OPS.JOIN] = function (docId, connId, name) {
        this.loaded[docId].cb.set_name(connId, name);
    };

    cerebro.NeuronClient = NeuronClient;
})();
