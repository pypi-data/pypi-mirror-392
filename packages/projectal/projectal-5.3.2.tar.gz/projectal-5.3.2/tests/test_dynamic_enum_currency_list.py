import projectal
from projectal.enums import Currency
from tests.base_test import BaseTest


class TestCurrencyList(BaseTest):
    def tearDown(self):
        default_currency_list = {
            Currency.AED: 784,
            Currency.ARS: 32,
            Currency.AUD: 36,
            Currency.BGN: 975,
            Currency.BRL: 986,
            Currency.CAD: 124,
            Currency.CHF: 756,
            Currency.CLP: 152,
            Currency.CNY: 156,
            Currency.COP: 170,
            Currency.CZK: 203,
            Currency.DKK: 208,
            Currency.EUR: 978,
            Currency.GBP: 826,
            Currency.HKD: 344,
            Currency.HUF: 348,
            Currency.IDR: 360,
            Currency.ILS: 376,
            Currency.INR: 356,
            Currency.JPY: 392,
            Currency.KRW: 410,
            Currency.MXN: 484,
            Currency.MYR: 458,
            Currency.NOK: 578,
            Currency.NZD: 554,
            Currency.PEN: 604,
            Currency.PHP: 608,
            Currency.PKR: 586,
            Currency.PLN: 985,
            Currency.RON: 946,
            Currency.RUB: 643,
            Currency.SAR: 682,
            Currency.SEK: 752,
            Currency.SGD: 702,
            Currency.THB: 764,
            Currency.TRY: 949,
            Currency.TWD: 901,
            Currency.UAH: 980,
            Currency.USD: 840,
            Currency.ZAR: 710,
            # remove potentially added currencies
            "ZWL": -932,
        }

        projectal.CurrencyList.set(default_currency_list)

    def test_currency_list_get_default_values(self):
        currency_list = projectal.CurrencyList.get()

        assert len(currency_list) == 40
        assert currency_list[Currency.AED] == 784
        assert currency_list[Currency.ARS] == 32
        assert currency_list[Currency.AUD] == 36
        assert currency_list[Currency.BGN] == 975
        assert currency_list[Currency.BRL] == 986
        assert currency_list[Currency.CAD] == 124
        assert currency_list[Currency.CHF] == 756
        assert currency_list[Currency.CLP] == 152
        assert currency_list[Currency.CNY] == 156
        assert currency_list[Currency.COP] == 170
        assert currency_list[Currency.CZK] == 203
        assert currency_list[Currency.DKK] == 208
        assert currency_list[Currency.EUR] == 978
        assert currency_list[Currency.GBP] == 826
        assert currency_list[Currency.HKD] == 344
        assert currency_list[Currency.HUF] == 348
        assert currency_list[Currency.IDR] == 360
        assert currency_list[Currency.ILS] == 376
        assert currency_list[Currency.INR] == 356
        assert currency_list[Currency.JPY] == 392
        assert currency_list[Currency.KRW] == 410
        assert currency_list[Currency.MXN] == 484
        assert currency_list[Currency.MYR] == 458
        assert currency_list[Currency.NOK] == 578
        assert currency_list[Currency.NZD] == 554
        assert currency_list[Currency.PEN] == 604
        assert currency_list[Currency.PHP] == 608
        assert currency_list[Currency.PKR] == 586
        assert currency_list[Currency.PLN] == 985
        assert currency_list[Currency.RON] == 946
        assert currency_list[Currency.RUB] == 643
        assert currency_list[Currency.SAR] == 682
        assert currency_list[Currency.SEK] == 752
        assert currency_list[Currency.SGD] == 702
        assert currency_list[Currency.THB] == 764
        assert currency_list[Currency.TRY] == 949
        assert currency_list[Currency.TWD] == 901
        assert currency_list[Currency.UAH] == 980
        assert currency_list[Currency.USD] == 840
        assert currency_list[Currency.ZAR] == 710

    def test_currency_list_set_currency_add(self):
        currency_list_add_currency = {
            Currency.AED: 784,
            Currency.ARS: 32,
            Currency.AUD: 36,
            Currency.BGN: 975,
            Currency.BRL: 986,
            Currency.CAD: 124,
            Currency.CHF: 756,
            Currency.CLP: 152,
            Currency.CNY: 156,
            Currency.COP: 170,
            Currency.CZK: 203,
            Currency.DKK: 208,
            Currency.EUR: 978,
            Currency.GBP: 826,
            Currency.HKD: 344,
            Currency.HUF: 348,
            Currency.IDR: 360,
            Currency.ILS: 376,
            Currency.INR: 356,
            Currency.JPY: 392,
            Currency.KRW: 410,
            Currency.MXN: 484,
            Currency.MYR: 458,
            Currency.NOK: 578,
            Currency.NZD: 554,
            Currency.PEN: 604,
            Currency.PHP: 608,
            Currency.PKR: 586,
            Currency.PLN: 985,
            Currency.RON: 946,
            Currency.RUB: 643,
            Currency.SAR: 682,
            Currency.SEK: 752,
            Currency.SGD: 702,
            Currency.THB: 764,
            Currency.TRY: 949,
            Currency.TWD: 901,
            Currency.UAH: 980,
            Currency.USD: 840,
            Currency.ZAR: 710,
            # Add currency: "ZWL"
            "ZWL": 932,
        }
        projectal.CurrencyList.set(currency_list_add_currency)
        updated_currency_list = projectal.CurrencyList.get()

        assert len(updated_currency_list) == len(currency_list_add_currency)

        for k, v in currency_list_add_currency.items():
            assert updated_currency_list[k] == v

    def test_currency_list_set_currency_delete(self):
        currency_list_delete_currency = {
            Currency.AED: 784,
            Currency.ARS: 32,
            Currency.AUD: 36,
            Currency.BGN: 975,
            Currency.BRL: 986,
            Currency.CAD: 124,
            Currency.CHF: 756,
            Currency.CLP: 152,
            Currency.CNY: 156,
            Currency.COP: 170,
            Currency.CZK: 203,
            Currency.DKK: 208,
            Currency.EUR: 978,
            Currency.GBP: 826,
            Currency.HKD: 344,
            Currency.HUF: 348,
            Currency.IDR: 360,
            Currency.ILS: 376,
            Currency.INR: 356,
            Currency.JPY: 392,
            Currency.KRW: 410,
            Currency.MXN: 484,
            Currency.MYR: 458,
            Currency.NOK: 578,
            Currency.NZD: 554,
            Currency.PEN: 604,
            Currency.PHP: 608,
            Currency.PKR: 586,
            Currency.PLN: 985,
            Currency.RON: 946,
            Currency.RUB: 643,
            Currency.SAR: 682,
            Currency.SEK: 752,
            Currency.SGD: 702,
            Currency.THB: 764,
            Currency.TRY: 949,
            Currency.TWD: 901,
            Currency.UAH: 980,
            Currency.USD: 840,
            # "ZAR" removed
            Currency.ZAR: -710,
        }
        projectal.CurrencyList.set(currency_list_delete_currency)
        updated_currency_list = projectal.CurrencyList.get()
        currency_list_delete_currency.pop(Currency.ZAR)

        assert len(updated_currency_list) == len(currency_list_delete_currency)

        for k, v in currency_list_delete_currency.items():
            assert updated_currency_list[k] == v
