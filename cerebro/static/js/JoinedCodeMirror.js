(function () {
    if (typeof window.cerebro === "undefined") {
        window.cerebro = {};
    }

    var cerebro = window.cerebro;

    function JoinedCodeMirror (el, options) {
        this.el = el;
        this.children = [];
        this.options = options || {};
    }

    JoinedCodeMirror.prototype = {
        constructor: JoinedCodeMirror,

        _makeJoinedCodeMirror: function (el) {
            var self = this;

            // XXX: cursorCoords . coordsChar . cursorCoords != coordsChar,
            //      so we take the vertical midpoint to ensure we choose the
            //      correct point.
            function midpointV (x) {
                return Math.floor((x.top + x.bottom) / 2);
            }

            var cm = CodeMirror(el, _.extend({
                    lineNumbers: true,
                    viewportMargin: Infinity,
                    lineWrapping: true
            }, this.options));
            cm.on("focus", function (o) {
                self.children.forEach(function (p) {
                    if (o !== p) {
                        p.setCursor(p.getCursor());
                    }
                })
            });
            cm.on("keydown", function (o, e) {
                if (e.shiftKey) {
                    // don't allow selection across multiple codemirrors
                    // (because that really doesn't work)
                    return;
                }

                var i = self.children.indexOf(o);

                var handled = false;
                var c = o.getCursor();
                var coords = o.cursorCoords(c, "div");

                switch (e.which) {
                    case 38: // UP ARROW
                        if (i > 0 && coords.top <= o.cursorCoords({
                            line: o.firstLine(),
                            ch: 0
                        }, "div").top) {
                            var p = self.children[i - 1];

                            var gc = o.doc.sel.goalColumn != null ? o.doc.sel.goalColumn
                                                                  : o.cursorCoords(c, "div").left;

                            p.setCursor({
                                ch: p.coordsChar({
                                    left: Math.max(gc, coords.left),
                                    top: midpointV(p.cursorCoords({
                                        line: p.lastLine()
                                    }, "div"))
                                }, "div").ch,
                                line: p.lastLine()
                            });

                            p.doc.sel.goalColumn = gc;
                            handled = true;
                        }
                        break;
                    case 40: // DOWN ARROW
                        if (i + 1 < self.children.length && coords.bottom >= o.cursorCoords({
                            line: o.lastLine()
                        }, "div").bottom) {
                            var p = self.children[i + 1];

                            var gc = o.doc.sel.goalColumn != null ? o.doc.sel.goalColumn
                                                                  : o.cursorCoords(c, "div").left;
                            p.setCursor({
                                ch: p.coordsChar({
                                    left: Math.max(gc, coords.left),
                                    top: midpointV(p.cursorCoords({
                                        line: p.firstLine(),
                                        ch: 0
                                    }, "div"))
                                }, "div").ch,
                                line: p.firstLine()
                            });

                            p.doc.sel.goalColumn = gc;
                            handled = true;
                        }
                        break;
                }

                if (handled) {
                    e.preventDefault();

                    o.setCursor(o.getCursor());

                    // prevent jumpiness on chrome
                    var x = window.scrollX;
                    var y = window.scrollY;
                    p.focus();
                    window.scrollTo(x, y);
                }
            });
            return cm;
        },

        addAtBack: function () {
            var self = this;
            var cm = this._makeJoinedCodeMirror(function (el) {
                self.el.appendChild(el);
            });
            this.children.push(cm);
            return cm;
        },

        addBefore: function (i) {
            var self = this;
            var cm = this._makeJoinedCodeMirror(function (el) {
                self.el.insertBefore(el, self.children[i].getWrapperElement());
            });
            this.children.splice(i, 0, cm);
            return cm;
        },

        remove: function (i) {
            var x = this.children.splice(i, 1);
            var el = x[0].getWrapperElement();
            el.parentNode.removeChild(el);
        }
    }

    cerebro.JoinedCodeMirror = JoinedCodeMirror;
})();
