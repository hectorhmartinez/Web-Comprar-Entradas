webpackJsonp([1],{"3uiE":function(t,e,a){t.exports=a.p+"static/img/lol.ffeab06.jpg"},"6sAc":function(t,e,a){t.exports=a.p+"static/img/haikyuu.3e3f429.jpg"},CvVJ:function(t,e,a){t.exports=a.p+"static/img/Football.de25d84.jpg"},LDfJ:function(t,e,a){t.exports=a.p+"static/img/Futsal.136e262.jpg"},NHnr:function(t,e,a){"use strict";Object.defineProperty(e,"__esModule",{value:!0});var n=a("Tqaz"),s=(a("sWs5"),a("7+uW")),o={render:function(){var t=this.$createElement;return(this._self._c||t)("router-view")},staticRenderFns:[]};var r=a("VU/8")({name:"App"},o,!1,function(t){a("qeOu")},null,null).exports,i=a("/ocq"),c=a("//Fk"),l=a.n(c),u=a("mtWM"),d=a.n(u),h={data:function(){return{cart_button_text:"Veure cistella",login_button_text:"Log in",is_showing_cart:!1,money_available:null,matches_added:[],matches:[],logged:!1,username:null,token:null,is_admin:!1}},methods:{buyTicket:function(t){var e=this.getIndexFromMatch(t);e>-1?this.matches_added[e].quantity+=1:console.error("Item not found (buyTicket)"),this.money_available=this.money_available-this.matches_added[e].match.price},returnTicket:function(t){var e=this.getIndexFromMatch(t);e>-1?this.matches_added[e].quantity-=1:console.error("Item not found (returnTicket)"),this.money_available=this.money_available+this.matches_added[e].match.price},toggleCartView:function(){this.is_showing_cart?(this.cart_button_text="Veure cistella ",this.is_showing_cart=!1):(this.cart_button_text="Tancar cistella",this.is_showing_cart=!0)},addEventToCart:function(t){this.matches_added.push({match:t,quantity:1})},removeEventFromCart:function(t){var e=this.getIndexFromMatch(t.match);e>-1?this.matches_added.splice(e,1):console.error("Item not found (removeEventFromCart)"),this.money_available+=t.match.price*t.quantity},getIndexFromMatch:function(t){return this.matches_added.map(function(t){return t.match.id}).indexOf(t.id)},addPurchase:function(t){var e=this;d.a.post("https://b06-sportsmaster.herokuapp.com/orders/"+this.username,{orders:t},{auth:{username:this.token}}).then(function(){console.log("Order done")}).catch(function(t){console.log(t),e.getMatches()})},finalizePurchase:function(){for(var t=[],e=0;e<this.matches_added.length;e+=1)t.push({match_id:this.matches_added[e].match.id,tickets_bought:this.matches_added[e].quantity});console.log(t),this.addPurchase(t),this.matches_added=[]},getMatches:function(){var t=this;d.a.get("https://b06-sportsmaster.herokuapp.com/matches").then(function(e){for(var a=e.data.matches.filter(function(t){return null!=t.competition_id}),n=[],s=function(t){var e=d.a.get("https://b06-sportsmaster.herokuapp.com/competition/"+a[t].competition_id).then(function(e){delete a[t].competition_id,a[t].competition={name:e.data.competition.name,category:e.data.competition.category,sport:e.data.competition.sport}}).catch(function(t){console.error(t)});n.push(e)},o=0;o<a.length;o++)s(o);l.a.all(n).then(function(e){console.log(a),t.matches=a})}).catch(function(t){console.error(t)})},getAccount:function(){var t=this;d.a.get("https://b06-sportsmaster.herokuapp.com/account/"+this.username).then(function(e){t.is_admin=e.data.account.is_admin,t.money_available=e.data.account.available_money.toFixed(2)}).catch(function(t){console.error(t)})},logIn_logOut:function(){this.logged?this.logOut():this.$router.push({path:"/userlogin"})},logOut:function(){this.logged=!1,this.username=null,this.token=null,this.is_admin=!1,this.login_button_text="Log In"}},created:function(){this.getMatches(),this.logged="true"===this.$route.query.logged,this.username=this.$route.query.username,this.token=this.$route.query.token,void 0===this.logged&&(this.logged=!1),this.logged&&(this.getAccount(),this.login_button_text="Log Out")}},m={render:function(){var t=this,e=t.$createElement,n=t._self._c||e;return n("div",{attrs:{id:"app"}},[n("div",{staticClass:"row",staticStyle:{"background-color":"#ffffff"}},[t._m(0),t._v(" "),n("div",{staticClass:"col"},[t.logged?n("b",[t._v("👤 "+t._s(t.username)+" 💰 "+t._s(t.money_available)+"\n        "),n("button",{staticClass:"btn btn-outline-primary btn-lg",on:{click:t.toggleCartView}},[t._v("\n          "+t._s(t.cart_button_text)+"\n          "),n("button",{staticClass:"btn btn-primary btn-sm"},[t._v(" "+t._s(t.matches_added.length))])]),t._v(" "),n("button",{staticClass:"btn btn-outline-success btn-lg",on:{click:t.logIn_logOut}},[t._v(" "+t._s(t.login_button_text))])]):n("b",[n("button",{staticClass:"btn btn-outline-primary btn-lg",on:{click:t.toggleCartView}},[t._v("\n          "+t._s(t.cart_button_text)+"\n          "),n("button",{staticClass:"btn btn-primary btn-sm"},[t._v(" "+t._s(t.matches_added.length))])]),t._v(" "),n("button",{staticClass:"btn btn-outline-success btn-lg",on:{click:t.logIn_logOut}},[t._v(" "+t._s(t.login_button_text))])])])]),t._v(" "),n("hr",{staticStyle:{"margin-top":"0px"}}),t._v(" "),t.is_showing_cart?n("div",{staticClass:"container",staticStyle:{"background-color":"#ffffff"}},[n("h1",[t._v(" Cart ")]),t._v(" "),t.matches_added.length>0?n("table",{staticClass:"table"},[t._m(1),t._v(" "),n("tbody",t._l(t.matches_added,function(e){return n("tr",{key:e.match.id},[n("td",[t._v(t._s(e.match.competition.sport))]),t._v(" "),n("td",[t._v(t._s(e.match.competition.name))]),t._v(" "),n("td",[t._v(t._s(e.match.local.name)+" vs "+t._s(e.match.visitor.name))]),t._v(" "),n("td",[t._v("\n          "+t._s(e.quantity)+"\n          "),n("button",{staticClass:"btn btn-success btn-sm",attrs:{disabled:t.money_available<=e.match.price},on:{click:function(a){return t.buyTicket(e.match)}}},[t._v(" +\n          ")]),t._v(" "),n("button",{staticClass:"btn btn-danger btn-sm",attrs:{disabled:e.quantity<2},on:{click:function(a){return t.returnTicket(e.match)}}},[t._v(" -\n          ")])]),t._v(" "),n("td",[t._v(t._s(e.match.price))]),t._v(" "),n("td",[t._v(t._s((e.match.price*e.quantity).toFixed(2)))]),t._v(" "),n("td",[n("button",{staticClass:"btn btn-danger",on:{click:function(a){return t.removeEventFromCart(e)}}},[t._v(" Eliminar entrada")])])])}),0)]):n("h3",[t._v(" Your cart is currently empty.")]),t._v(" "),n("button",{staticClass:"btn btn-secondary btn-lg",on:{click:t.toggleCartView}},[t._v(" Enrere")]),t._v(" "),n("button",{staticClass:"btn btn-success btn-lg",attrs:{disabled:t.matches_added.length<1},on:{click:function(e){return t.finalizePurchase()}}},[t._v("\n      Finalitzar la compra\n    ")])]):n("div",{staticClass:"container"},[n("div",{staticClass:"row"},t._l(t.matches,function(e){return n("div",{key:e.id,staticClass:"col-lg-4 col-md-6 mb-4"},[n("div",{staticClass:"card",staticStyle:{width:"18rem"}},["Volleyball"!==e.competition.sport||"Karasuno"!==e.local.name&&"Karasuno"!==e.visitor.name?n("img",{staticClass:"card-img-top",attrs:{src:a("vvha")("./"+e.competition.sport+".jpg")}}):n("img",{staticClass:"card-img-top",attrs:{src:a("6sAc"),alt:"Card image cap"}}),t._v(" "),n("div",{staticClass:"card-body"},[n("h5",{staticClass:"card-title"},[t._v(t._s(e.competition.sport)+" - "+t._s(e.competition.category))]),t._v(" "),n("h6",{staticClass:"card-text"},[t._v(t._s(e.competition.name))]),t._v(" "),n("h6",{staticClass:"card-text"},[n("strong",[t._v(t._s(e.local.name))]),t._v(" ("+t._s(e.local.country)+") vs\n              "),n("strong",[t._v(t._s(e.visitor.name))]),t._v(" ("+t._s(e.visitor.country)+")")]),t._v(" "),n("h6",{staticClass:"card-text"},[t._v(t._s(e.date.substring(0,10)))]),t._v(" "),n("h6",{staticClass:"card-text"},[t._v(t._s(e.price)+" €")]),t._v(" "),n("h6",{staticClass:"card-text"},[t._v(t._s(e.total_available_tickets)+" tickets available")]),t._v(" "),n("button",{staticClass:"btn btn-success btn-lg",on:{click:function(a){return t.addEventToCart(e)}}},[t._v(" Afegeix a la cistella")])])])])}),0)])])},staticRenderFns:[function(){var t=this.$createElement,e=this._self._c||t;return e("div",{staticClass:"col",staticStyle:{"text-align":"center","margin-right":"250px"}},[e("h1",[this._v("Sports Matches")])])},function(){var t=this,e=t.$createElement,a=t._self._c||e;return a("thead",[a("tr",[a("th",{attrs:{scope:"col"}},[t._v("Sport")]),t._v(" "),a("th",{attrs:{scope:"col"}},[t._v("Competition")]),t._v(" "),a("th",{attrs:{scope:"col"}},[t._v("Match")]),t._v(" "),a("th",{staticStyle:{width:"10rem"},attrs:{scope:"col"}},[t._v("Quantity")]),t._v(" "),a("th",{attrs:{scope:"col"}},[t._v("Price(€)")]),t._v(" "),a("th",{attrs:{scope:"col"}},[t._v("Total")]),t._v(" "),a("th",{attrs:{scope:"col"}})])])}]},p=a("VU/8")(h,m,!1,null,null,null).exports,_={data:function(){return{logged:!1,username:null,password:null,token:null,creatingAccount:!1,addUserForm:{username:null,password:null}}},methods:{checkLogin:function(){var t=this,e={username:this.username,password:this.password};d.a.post("https://b06-sportsmaster.herokuapp.com/login",e).then(function(e){t.logged=!0,t.token=e.data.token,t.$router.push({path:"/",query:{username:t.username,logged:t.logged,token:t.token}})}).catch(function(t){console.error(t),alert("Username or Password incorrect")})},backToLogin:function(){this.creatingAccount=!1,this.username=null,this.password=null},initCreateForm:function(){this.creatingAccount=!0,this.addUserForm.username=null,this.addUserForm.password=null},createAccount:function(){var t=this,e={username:this.addUserForm.username,password:this.addUserForm.password};d.a.post("https://b06-sportsmaster.herokuapp.com/account",e).then(function(){console.log("Account created"),alert("Account created"),t.backToMatches()}).catch(function(t){console.log(t),alert(t.response.data.message)})},backToMatches:function(){this.$router.push({path:"/"})}},created:function(){this.logged="true"===this.$route.query.logged,this.username=this.$route.query.username,this.token=this.$route.query.token,void 0===this.logged&&(this.logged=!1)}},g={render:function(){var t=this,e=t.$createElement,a=t._self._c||e;return a("div",{attrs:{id:"app"}},[t._m(0),t._v(" "),a("hr",{staticStyle:{"margin-top":"0px"}}),t._v(" "),a("div",{staticClass:"w-25 container",staticStyle:{"background-color":"#ffffff"}},[a("hr",{staticStyle:{"margin-top":"90px","border-color":"#ffffff"}}),t._v(" "),t.creatingAccount?a("h2",[t._v("Create Account")]):a("h2",[t._v("Login")]),t._v(" "),a("b-form",[a("b-form-group",{attrs:{label:"Username","label-for":"inputUsername","label-align":"left"}},[t.creatingAccount?a("b-form-input",{attrs:{id:"inputUsername",type:"text",placeholder:"Enter Username",required:""},model:{value:t.addUserForm.username,callback:function(e){t.$set(t.addUserForm,"username",e)},expression:"addUserForm.username"}}):a("b-form-input",{attrs:{id:"inputUsername",type:"text",placeholder:"Enter Username",required:""},model:{value:t.username,callback:function(e){t.username=e},expression:"username"}})],1),t._v(" "),a("b-form-group",{attrs:{label:"Password","label-for":"inputPassword","label-align":"left"}},[t.creatingAccount?a("b-form-input",{attrs:{id:"inputPassword",type:"password",placeholder:"Enter Password",required:""},model:{value:t.addUserForm.password,callback:function(e){t.$set(t.addUserForm,"password",e)},expression:"addUserForm.password"}}):a("b-form-input",{attrs:{id:"inputPassword",type:"password",placeholder:"Enter Password",required:""},model:{value:t.password,callback:function(e){t.password=e},expression:"password"}})],1),t._v(" "),t.creatingAccount?a("div",{staticClass:"d-grid col-form-label mx-auto"},[a("button",{staticClass:"btn btn-primary w-100",staticStyle:{"margin-top":"10px","font-size":"larger"},attrs:{type:"button"},on:{click:t.createAccount}},[t._v("\n          Submit\n        ")]),t._v(" "),a("button",{staticClass:"btn btn-secondary w-100",staticStyle:{"margin-top":"10px","font-size":"larger","margin-bottom":"20px"},attrs:{type:"button"},on:{click:t.backToLogin}},[t._v("\n          Back To Log In\n        ")])]):a("div",{staticClass:"d-grid col-form-label mx-auto"},[a("button",{staticClass:"btn btn-primary w-100",staticStyle:{"margin-top":"10px","font-size":"larger"},attrs:{type:"button"},on:{click:t.checkLogin}},[t._v("\n          Sign In\n        ")]),t._v(" "),a("button",{staticClass:"btn btn-success w-100",staticStyle:{"margin-top":"10px","font-size":"larger"},attrs:{type:"button"},on:{click:t.initCreateForm}},[t._v("\n          Create Account\n        ")]),t._v(" "),a("button",{staticClass:"btn btn-secondary w-100",staticStyle:{"margin-top":"10px","font-size":"larger","margin-bottom":"20px"},attrs:{type:"button"},on:{click:t.backToMatches}},[t._v("\n          Back To Matches\n        ")])])],1)],1)])},staticRenderFns:[function(){var t=this.$createElement,e=this._self._c||t;return e("div",{staticClass:"row",staticStyle:{"background-color":"#ffffff"}},[e("div",{staticClass:"col",staticStyle:{"text-align":"center","margin-right":"250px"}},[e("h1",[this._v("Sports Matches")])]),this._v(" "),e("div",{staticClass:"col"})])}]},v=a("VU/8")(_,g,!1,null,null,null).exports;s.default.use(i.a);var b=new i.a({mode:"history",base:Object({NODE_ENV:"production"}).BASE_URL,routes:[{path:"/",name:"Matches",component:p},{path:"/userlogin",name:"Login",component:v}]});s.default.use(n.a),s.default.config.productionTip=!1,new s.default({el:"#app",router:b,components:{App:r},template:"<App/>"})},epGR:function(t,e,a){t.exports=a.p+"static/img/Basketball.f2892a0.jpg"},q3qk:function(t,e,a){t.exports=a.p+"static/img/Volleyball.845101b.jpg"},qeOu:function(t,e){},sWs5:function(t,e){},uKLf:function(t,e,a){t.exports=a.p+"static/img/furbo.97c11e3.jpg"},vvha:function(t,e,a){var n={"./Basketball.jpg":"epGR","./Football.jpg":"CvVJ","./Futsal.jpg":"LDfJ","./Volleyball.jpg":"q3qk","./furbo.jpg":"uKLf","./haikyuu.jpg":"6sAc","./lol.jpg":"3uiE"};function s(t){return a(o(t))}function o(t){var e=n[t];if(!(e+1))throw new Error("Cannot find module '"+t+"'.");return e}s.keys=function(){return Object.keys(n)},s.resolve=o,t.exports=s,s.id="vvha"}},["NHnr"]);
//# sourceMappingURL=app.af31179bd2220ba18210.js.map