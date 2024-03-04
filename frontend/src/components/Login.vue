<template>
  <div id="app">
    <!-- Capçalera -->
    <div class="row" style="background-color:#ffffff">
      <div class="col" style="text-align:center; margin-right: 250px">
        <h1>Sports Matches</h1>
      </div>
      <div class="col">
      </div>
    </div>
    <hr style="margin-top: 0px"/>
    <!-- Cos -->
    <div class="w-25 container" style="background-color: #ffffff; ">
      <hr style="margin-top: 90px; border-color: #ffffff"/>
      <h2 v-if="creatingAccount">Create Account</h2>
      <h2 v-else>Login</h2>
      <b-form>
        <!-- Username label -->
        <b-form-group
          label="Username"
          label-for="inputUsername"
          label-align="left"
        >
          <!-- CREATE ACCOUNT username input -->
          <b-form-input
            v-if="creatingAccount"
            id="inputUsername"
            v-model="addUserForm.username"
            type="text"
            placeholder="Enter Username"
            required>
          </b-form-input>
          <!-- LOGIN username input -->
          <b-form-input
            v-else
            id="inputUsername"
            v-model="username"
            type="text"
            placeholder="Enter Username"
            required>
          </b-form-input>
        </b-form-group>
        <!-- Password label-->
        <b-form-group
          label="Password"
          label-for="inputPassword"
          label-align="left"
        >
          <!-- CREATE ACCOUNT password input -->
          <b-form-input
            v-if="creatingAccount"
            id="inputPassword"
            v-model="addUserForm.password"
            type="password"
            placeholder="Enter Password"
            required>
          </b-form-input>
          <!-- LOGIN password input -->
          <b-form-input
            v-else
            id="inputPassword"
            v-model="password"
            type="password"
            placeholder="Enter Password"
            required>
          </b-form-input>

        </b-form-group>
        <!-- CREATE ACCOUNT -->
        <div v-if="creatingAccount" class="d-grid col-form-label mx-auto">
          <button type="button" class="btn btn-primary w-100"
                  style="margin-top: 10px; font-size: larger;" @click="createAccount">
            Submit
          </button>
          <button type="button" class="btn btn-secondary w-100"
                  style="margin-top: 10px; font-size: larger; margin-bottom: 20px" @click="backToLogin">
            Back To Log In
          </button>
        </div>
        <!-- LOGIN -->
        <div v-else class="d-grid col-form-label mx-auto">
          <button type="button" class="btn btn-primary w-100"
                  style="margin-top: 10px; font-size: larger;" @click="checkLogin">
            Sign In
          </button>
          <button type="button" class="btn btn-success w-100"
                  style="margin-top: 10px; font-size: larger;" @click="initCreateForm">
            Create Account
          </button>
          <button type="button" class="btn btn-secondary w-100"
                  style="margin-top: 10px; font-size: larger; margin-bottom: 20px" @click="backToMatches">
            Back To Matches
          </button>
        </div>
      </b-form>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data () {
    return {
      logged: false,
      username: null,
      password: null,
      token: null,
      creatingAccount: false,
      addUserForm: {
        username: null,
        password: null
      }
    }
  },
  methods: {
    checkLogin () {
      const parameters = {
        username: this.username,
        password: this.password
      }
      const path = 'https://b06-sportsmaster.herokuapp.com/login'
      axios.post(path, parameters)
        .then((res) => {
          this.logged = true
          this.token = res.data.token
          this.$router.push({path: '/', query: {username: this.username, logged: this.logged, token: this.token}})
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error)
          alert('Username or Password incorrect')
        })
    },
    backToLogin () {
      this.creatingAccount = false
      this.username = null
      this.password = null
    },
    initCreateForm () {
      this.creatingAccount = true
      this.addUserForm.username = null
      this.addUserForm.password = null
    },
    createAccount () {
      const path = 'https://b06-sportsmaster.herokuapp.com/account'
      const parameters = {
        username: this.addUserForm.username,
        password: this.addUserForm.password
      }

      axios.post(path, parameters)
        .then(() => {
          console.log('Account created')
          alert('Account created')
          // Per fer login automatic amb el checkLogin
          this.username = parameters.username
          this.password = parameters.password
          this.checkLogin()
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error)
          alert(error.response.data.message)
        })
    },
    backToMatches () {
      this.$router.push({path: '/'})
    }
  },
  created () {
    this.logged = this.$route.query.logged === 'true'
    this.username = this.$route.query.username
    this.token = this.$route.query.token
    if (this.logged === undefined) {
      this.logged = false
    }
  }
}
</script>
