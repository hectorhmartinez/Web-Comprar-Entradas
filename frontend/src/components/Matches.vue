<template>
  <div id="app">
    <!-- Capçalera -->
    <div class="row" style="background-color:#ffffff">
      <div class="col" style="text-align:center; margin-right: 249px">
        <h1>Sports Matches</h1>
      </div>
      <div class="col">
        <b v-if="logged">👤 {{ username }} &#128176; {{ money_available }}
          <button v-if="logged" class="btn btn-outline-primary btn-lg" @click="toggleCartView">
            {{ cart_button_text }}
            <button class="btn btn-primary btn-sm"> {{ matches_added.length }}</button>
          </button>
          <button class="btn btn-outline-success btn-lg" @click="logIn_logOut"> {{ login_button_text }}</button>
        </b>
        <b v-else>
          <button v-if="logged" class="btn btn-outline-primary btn-lg" @click="toggleCartView">
            {{ cart_button_text }}
            <button  class="btn btn-primary btn-sm"> {{ matches_added.length }}</button>
          </button>
          <button class="btn btn-outline-success btn-lg" @click="logIn_logOut"> {{ login_button_text }}</button>
        </b>
      </div>
    </div>
    <hr style="margin-top: 0px"/>
    <!-- Taula amb la informació per comprar entrades -->
    <div v-if="is_showing_cart" class="container" style="background-color:#ffffff">
      <h1> Cart </h1>
      <table v-if="matches_added.length > 0" class="table">
        <thead>
        <tr>
          <th scope="col">Sport</th>
          <th scope="col">Competition</th>
          <th scope="col">Match</th>
          <th scope="col" style="width: 10rem">Quantity</th>
          <th scope="col">Price(&euro;)</th>
          <th scope="col">Total</th>
          <th scope="col"></th>
        </tr>
        </thead>
        <tbody>
        <tr v-for="(pair) in matches_added" :key="pair.match.id">
          <td>{{ pair.match.competition.sport }}</td>
          <td>{{ pair.match.competition.name }}</td>
          <td>{{ pair.match.local.name }} vs {{ pair.match.visitor.name }}</td>
          <td>
            {{ pair.quantity }}
            <button class="btn btn-success btn-sm" @click="buyTicket(pair.match)"> +
            </button>
            <button class="btn btn-danger btn-sm" @click="returnTicket(pair.match)" :disabled="pair.quantity < 2"> -
            </button>
          </td>
          <td>{{ pair.match.price }}</td>
          <td>{{ (pair.match.price * pair.quantity).toFixed(2) }}</td>
          <td>
            <button class="btn btn-danger" @click="removeEventFromCart(pair)"> Eliminar entrada</button>
          </td>
        </tr>
        </tbody>
      </table>
      <h3 v-else> Your cart is currently empty.</h3>
      <button class="btn btn-secondary btn-lg" @click="toggleCartView"> Enrere</button>
      <button class="btn btn-success btn-lg" @click="finalizePurchase()" :disabled="matches_added.length < 1">
        Finalitzar la compra
      </button>
    </div>
    <div v-else class="container">
      <!-- Cards representant els partits -->
      <div class="row">
        <div class="col-lg-4 col-md-6 mb-4" v-for="(match) in matches" :key="match.id">
          <div class="card" style="width: 18rem;">
            <!-- Imatge del partit -->
            <img class="card-img-top"
                 v-if="(match.competition.sport) === 'Volleyball' && (match.local.name === 'Karasuno' || match.visitor.name === 'Karasuno')"
                 src="@/assets/haikyuu.jpg" alt="Card image cap">
            <img class="card-img-top" v-else v-bind:src="require('@/assets/' + match.competition.sport + '.jpg')">
            <!-- Info dels partits -->
            <div class="card-body">
              <h5 class="card-title">{{ match.competition.sport }} - {{ match.competition.category }}</h5>
              <h6 class="card-text">{{ match.competition.name }}</h6>
              <h6 class="card-text"><strong>{{ match.local.name }}</strong> ({{ match.local.country }}) vs
                <strong>{{ match.visitor.name }}</strong> ({{ match.visitor.country }})</h6>
              <h6 class="card-text">{{ match.date.substring(0, 10) }}</h6>
              <h6 class="card-text">{{ match.price }} &euro;</h6>
              <h6 class="card-text">{{ match.total_available_tickets }} tickets available</h6>

              <button class="btn btn-success btn-lg" @click="addEventToCart(match)" :disabled="!logged"> Afegeix a la cistella</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data () {
    return {
      cart_button_text: 'Veure cistella',
      login_button_text: 'Log in',
      is_showing_cart: false,
      money_available: null,
      matches_added: [],
      matches: [],
      logged: false,
      username: null,
      token: null,
      is_admin: false
    }
  },
  methods: {
    buyTicket (match) {
      const index = this.getIndexFromMatch(match)
      if (index > -1) {
        this.matches_added[index].quantity += 1
      } else {
        console.error('Item not found (buyTicket)')
      }
    },
    returnTicket (match) {
      const index = this.getIndexFromMatch(match)
      if (index > -1) {
        this.matches_added[index].quantity -= 1
      } else {
        console.error('Item not found (returnTicket)')
      }
    },
    toggleCartView () {
      if (this.is_showing_cart) {
        this.cart_button_text = 'Veure cistella '
        this.is_showing_cart = false
      } else {
        this.cart_button_text = 'Tancar cistella'
        this.is_showing_cart = true
      }
    },
    addEventToCart (match) {
      const quantity = 1
      // if match is not in matches_added
      if (this.getIndexFromMatch(match) === -1) {
        this.matches_added.push({match, quantity})
      } else {
        this.buyTicket(match)
      }
    },
    removeEventFromCart (pair) {
      const index = this.getIndexFromMatch(pair.match)
      if (index > -1) {
        this.matches_added.splice(index, 1)
      } else {
        console.error('Item not found (removeEventFromCart)')
      }
    },
    getIndexFromMatch (match) {
      return this.matches_added.map(function (o) {
        return o.match.id
      }).indexOf(match.id)
    },
    addPurchase (parameters) {
      const path = 'https://b06-sportsmaster.herokuapp.com/orders/'
      axios.post(path + this.username, {'orders': parameters}, {
        auth: {username: this.token}
      })
        .then(() => {
          alert('Order done')
        })
        .catch((error) => {
          // eslint-disable-next-line
          alert(error.response.data.message)
          this.getMatches()
        })
    },
    finalizePurchase () {
      const parameters = []
      for (let i = 0; i < this.matches_added.length; i += 1) {
        parameters.push({
          'match_id': this.matches_added[i].match.id,
          'tickets_bought': this.matches_added[i].quantity
        })
      }
      // TODO: potser mirar aqui els diners tmb ara q els tenim
      this.addPurchase(parameters)
      this.matches_added = []
      // update dineros
      setTimeout(() => this.getAccount(), 500)
    },
    getMatches () {
      const pathMatches = 'https://b06-sportsmaster.herokuapp.com/matches'
      const pathCompetition = 'https://b06-sportsmaster.herokuapp.com/competition/'

      axios.get(pathMatches)
        .then((res) => {
          var matches = res.data.matches.filter((match) => {
            return match.competition_id != null
          })
          var promises = []
          for (let i = 0; i < matches.length; i++) {
            const promise = axios.get(pathCompetition + matches[i].competition_id)
              .then((resCompetition) => {
                delete matches[i].competition_id
                matches[i].competition = {
                  'name': resCompetition.data.competition.name,
                  'category': resCompetition.data.competition.category,
                  'sport': resCompetition.data.competition.sport
                }
              })
              .catch((error) => {
                console.error(error)
              })
            promises.push(promise)
          }
          Promise.all(promises).then((_) => {
            console.log(matches)
            this.matches = matches
          })
        })
        .catch((error) => {
          console.error(error)
        })
    },
    getAccount () {
      const pathAccount = 'https://b06-sportsmaster.herokuapp.com/account/'

      axios.get(pathAccount + this.username)
        .then((res) => {
          this.is_admin = res.data.account.is_admin
          this.money_available = res.data.account.available_money.toFixed(2)
        })
        .catch((error) => {
          console.error(error.response.data.message)
          alert(error.response.data.message)
        })
    },
    logIn_logOut () {
      // volem fer logout
      if (this.logged) {
        this.logOut()
      } else {
        this.$router.push({path: '/userlogin'})
      }
    },
    logOut () {
      this.logged = false
      this.username = null
      this.token = null
      this.is_admin = false
      this.login_button_text = 'Log In'
    }
  },
  created () {
    this.getMatches()
    this.logged = this.$route.query.logged === 'true'
    this.username = this.$route.query.username
    this.token = this.$route.query.token
    if (this.logged === undefined) {
      this.logged = false
    }
    if (this.logged) {
      this.getAccount()
      this.login_button_text = 'Log Out'
    }
  }
}

</script>
