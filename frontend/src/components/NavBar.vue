<template>
  <div class="navigation" :class="{'dark': !isDark}">
    <ul>
        <li v-for="value in items" :key="value.to" class="list" :class="{active: isActive(value.to)}" >
            <RouterLink  :to="value.to">
                <span class="icon">
                    <ion-icon :name="value.icon "></ion-icon>
                </span>
                <span class="text">{{ value.label }}</span>
            </RouterLink>
        </li>
        <div class="indicator">
        </div>
    </ul>
  </div>
</template>

<script>
export default {
  name: 'NavBar',
  props:{
    isDark: {
      type: Boolean,
      required: true,
    },
  },
  data() {
    return {
      items: [
        { to: '/',                  icon: 'home-outline',                label: 'Организации' },
        { to: '/users/',            icon: 'person-outline',              label: 'Пользователи' },
        { to: '/search-documents/', icon: 'chatbubble-ellipses-outline', label: 'Поиск писем' },
        { to: '/statistika/',       icon: 'analytics-outline',           label: 'Статистика' },
        { to: '/account/',          icon: 'settings-outline',            label: 'Аккаунт' },
      ],

    }
  },
  computed: {
    activeIndex() {
      const norm = p => String(p || '').replace(/\/+$/, '')
      const i = this.items.findIndex(x => norm(x.to) === norm(this.$route.path))
      return i === -1 ? 0 : i
    },
  },
  methods: {
      isActive(to) {
      const norm = p => String(p || '').replace(/\/+$/, '')
      return norm(this.$route.path) === norm(to)
    },
  },
}
</script>

<style scoped>
.navigation{
    bottom: 0;
    left: 50%;
    transform: translateX(-50%);
    position: absolute;
    width: 600px;
    height: 70px;
    background: #fff;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 10px;
    z-index: 50;
}
.navigation ul{
    display: flex;
    width: 550px;
}
.navigation ul li{
position: relative;
width: 130px;
height: 70px;
z-index: 1;
}
.navigation ul li a{
    position: relative;
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: column;
    width: 100%;
    text-align: center;
    font-weight: 500;

}
.navigation ul li a .icon{
    position: relative;
    display: block;
    line-height: 75px;
    font-size: 1.5em;
    text-align: center;
    transition: 0.5s;
    color: var(--clr);
}
.navigation ul li.active a .icon{
    transform: translateY(-32px);
}
.navigation ul li a .text{
    position: absolute;
    color:var(--clr);
    font-weight: 400;
    font-size: 0.75em;
    letter-spacing: 0.05em;
    transition: 0.5s;
    opacity: 0;
    transform: translateY(20px);
}
.navigation ul li.active a .text{
opacity: 1;
transform: translateY(10px);
}
.indicator{
    position: absolute;
    top: -50%;
    width: 70px;
    height: 70px;
    left: 45px;
    background: var(--button-green-dark);
    border-radius: 50%;
    border:7px solid var(--clr);
    transition: 0.5s;
}
.indicator::before{
    content: "";
    position: absolute;
    top: 50%;
    left: -22.5px;
    width: 20px;
    height: 20px;
    background: transparent;
    border-top-right-radius:20px;
    box-shadow: 0px -10px 0 0 var(--clr);
}
.indicator::after{
    content: "";
    position: absolute;
    top: 50%;
    right: -22.5px;
    width: 20px;
    height: 20px;
    background: transparent;
    border-top-left-radius:20px ;
    box-shadow:-1px -10px 0 0 var(--clr);
}
.navigation ul li:nth-child(1).active ~ .indicator{
    transform: translateX(calc(100px * 0));
}
.navigation ul li:nth-child(2).active ~ .indicator{
    transform: translateX(calc(110px * 1));
}
.navigation ul li:nth-child(3).active ~ .indicator{
    transform: translateX(calc(110px * 2));
}
.navigation ul li:nth-child(4).active ~ .indicator{
    transform: translateX(calc(110px * 3));
}
.navigation ul li:nth-child(5).active ~ .indicator{
    transform: translateX(calc(110px * 4));
}


.navigation.dark{
    background: var(--clr);
}
.navigation.dark ul li a .icon{
    color: white;
}
.navigation.dark ul li a .text{
    color: white;
}
.navigation.dark .indicator{
    border:7px solid white;

}
.navigation.dark .indicator::before,
.navigation.dark .indicator::after{
    box-shadow: 0px -10px 0 0 white;
}
</style>
