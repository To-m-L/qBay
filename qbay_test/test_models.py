from qbay.models import (register, login, update_user,
                         create_product, update_product, 
                         place_order, db)

# Global variable to test max character length of email local and domain
# while following Flake8 style guide (lines 79 characters or less)
long_str = 'yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyysyyyyyyyyyyyyyyyyyyyyyyyyyyyy'


def test_r1_1_user_register():
    '''
    Both the email and password cannot be empty.
    '''

    assert register('user', 'good@test.com', '@Password') is True
    assert register('user', '', '@Password') is False
    assert register('user', 'badpassword@test.com', '') is False
    assert register('user', '', '') is False


def test_r1_2_user_register():
    '''
    Testing R1-2: A user is uniquely identified by his/her email address.
    '''

    register('FoundUser', 'find.user@test.com', '@Password')
    user = login('find.user@test.com', '@Password')
    assert user.username == 'FoundUser'
    assert user.password == '@Password'


def test_r1_3_user_register():
    '''
    The email has to follow addr-spec defined in RFC 5322
    '''

    # local name tests
    assert register('testEmail', 'testemail@com', '@Password') is False
    assert register('testEmail', 'te..st@mail.com', '@Password') is False
    assert register('testEmail', '.test@mail.com', '@Password') is False
    assert register('testEmail', 'test.@mail.com', '@Password') is False
    assert register('testEmail', 'test.gg@mail.com', '@Password') is True
    assert register('u5', long_str + '@test.com', '@Password') is False
    assert register('user', '', '@Password') is False
    assert register('testEmail', 't!est.gg@mail.com', '@Password') is True
    assert register('testEmail', 't*est.gg@mail.com', '@Password') is True
    assert register('testEmail', '#est.gg@mail.com', '@Password') is True
    assert register('testEmail', '{t_est}.gg@mail.com', '@Password') is True
    assert register('testEmail', '"t!st.gg"@mail.com', '@Password') is True
    assert register('testEmail', '\" \"@mail.com', '@Password') is True
    assert register('testEmail', '"t!e"st.gg@mail.com', '@Password') is False
    assert register('testEmail', '"t!e"st.gg@mail.com', '@Password') is False
    assert register('testEmail', '"t!e"st" ".gg@ma.com', '@Password') is False
    assert register('testEmail', '""@mail.com', '@Password') is False

    # domain tests
    assert register('testEmail', 'test@-mail.com', '@Password') is False
    assert register('testEmail', 'test.@mail.com-', '@Password') is False
    assert register('u5', 'test@' + long_str + '.com', '@Password') is False
    assert register('testEmail', 'test.@ma..il.com', '@Password') is False
    assert register('testEmail', 'WOW@[192.168.2.1]', '@Password') is True
    assert register('testEmail', 'regexL@[192.300.2.1]', '@Password') is False
    assert register('testEmail', '''WOW@[2001:db8:0:1234:0:567:8:1]''',
                    '@Password') is True
    assert register('testEmail', 'WOW@[2001:db8::]', '@Password') is True
    assert register('testEmail', 'WOW@[::]', '@Password') is True
    assert register('testEmail', 'WOW@[::1234:5678]', '@Password') is True
    assert register('testEmail',
                    '''WOW@[2001:0db8:0001:0000:0000:0ab9:C0A8:0102]''',
                    '@Password') is True
    assert register('testEmail', '''WOW@[::1234:5678:91.123.4.56]''',
                    '@Password') is False
    assert register('testEmail', 'F@[IPv6:2001:db8::1]', '@Password') is False


def test_r1_4_user_register():
    '''
    Password has to meet the required complexity: minimum length 6,
    at least one upper case, at least one lower case, and at least
    one special character.
    '''

    assert register('user', 'TestPassword@test.com', '@Password') is True
    assert register('user', 'lowercasePassword@test.com', '@password') is False
    assert register('user', 'uppercasePassword@test.com', '@PASSWORD') is False
    assert register('user', 'specialPassword@test.com', 'Password') is False


def test_r1_5_user_register():
    '''
    User name has to be non-empty, alphanumeric-only,
    and space allowed only if it is not as the prefix or suffix.
    '''

    assert register('user', 'ValidUser@test.com', '@Password') is True
    assert register(' ', 'SpaceUser@test.com', '@Password') is False
    assert register('user@', 'SpecialPassword@test.com', '@PASSWORD') is False
    assert register(' user', 'SpaceFirst@test.com', '@Password') is False
    assert register('user ', 'SpaceLast@test.com', '@Password') is False
    assert register('us er', 'SpaceMiddle@test.com', '@Password') is True


def test_r1_6_user_register():
    '''
    Testing R1-6: User name has to be longer than 2 characters
    and less than 20 characters.
    '''

    assert register('2c', '2characters@test.com',
                    '@Password') is True
    assert register('exactly20characterss', '20characters@test.com',
                    '@Password') is True
    assert register('within2and20char', 'lessthan20and2@test.com',
                    '@Password') is True
    assert register('longerthan20characters', 'morethan20@test.com',
                    '@Password') is False
    assert register('1', '1character@test.com', '@Password') is False


def test_r1_7_user_register():
    '''
    Testing R1-7: If the email has been used, the operation failed.
    '''

    assert register('user', 'same.email@test.com', '@Password') is True
    assert register('user', 'unique@test.com', '@Password') is True
    assert register('user', 'same.email@test.com', '@Password') is False


def test_r1_8_user_register():
    '''
    Testing R1-8: Shipping address is empty at the time of registration.
    '''

    register('user', 'shipping@test.com', '@Password')
    user = login('shipping@test.com', '@Password')
    assert user.shipping_address is None


def test_r1_9_user_register():
    '''
    Testing R1-9: Postal code is empty at the time of registration.
    '''

    register('user', 'postal@test.com', '@Password')
    user = login('postal@test.com', '@Password')
    assert user.postal_code is None


def test_r1_10_user_register():
    '''
    Testing R1-9: Balance should be initialized as 100
    at the time of registration. (free $100 dollar signup bonus).
    '''

    register('BalanceUser', 'Balance.Test@test.com', '@Password')
    user = login('Balance.Test@test.com', '@Password')
    assert user.balance == 100


def test_r2_1_login():
    '''
    Testing R2-1: A user can log in using her/his email address
      and the password.
    (will be tested after the test_r1_10_user_register test, so we
    already have BalanceUser in database)
    '''

    user = login('Balance.Test@test.com', '@Password')
    assert user is not None
    assert user.username == 'BalanceUser'

    user = login('Balance.Test@test.com', '@BadPassword')
    assert user is None

    user = login('notemail@test.com', '@Password')
    assert user is None


def test_r2_2_login():
    '''
    Testing R2-2: The login function should check if the supplied
    inputs meet the same email/password requirements in the register
    function, before checking the database.
    '''

    assert login('', '@Password') is None
    assert login('badpassword@test.com', '') is None
    assert login('', '') is None

    assert login('lowercasePassword@test.com', '@password') is None
    assert login('uppercasePassword@test.com', '@PASSWORD') is None
    assert login('specialPassword@test.com', 'Password') is None

    user = login('Balance.Test@test.com', '@Password')
    assert user is not None
    assert user.username == 'BalanceUser'


def test_r3_1_update_user():
    '''
    Testing R3-1: A user is only able to update his/her user name,
    shipping_address, and postal_code.
    '''

    register('RandomUser', 'update.Test@test.com', '@Password')
    user = login('update.Test@test.com', '@Password')
    assert user.username == 'RandomUser'
    assert user.shipping_address is None
    assert user.postal_code is None
    assert update_user('update.Test@test.com', 'ModifiedUser',
                       'ModifiedShipping', 'K7L 2H9') is True
    assert user.username == 'ModifiedUser'
    assert user.shipping_address == 'ModifiedShipping'
    assert user.postal_code == 'K7L 2H9'


def test_r3_2_update_user():
    '''
    Testing R3-2: Shipping_address should be non-empty, alphanumeric-only,
    and no special characters such as !
    '''

    assert update_user('update.Test@test.com', None, 
                       'alphanumeric12only') is True
    assert update_user('update.Test@test.com', None, '',) is False
    assert update_user('update.Test@test.com', None, 
                       'specialchars!@}') is False


def test_r3_3_update_user():
    '''
    Testing R3-3: Postal code must be a valid Canadian postal code
    '''

    assert update_user('update.Test@test.com', None, None, 'M1C 8X3') is True
    assert update_user('update.Test@test.com', None, None, 'm1C 8X3') is False
    assert update_user('update.Test@test.com', None, None, 'D1C 8X3') is False
    assert update_user('update.Test@test.com', None, None, 'F1C 8X3') is False
    assert update_user('update.Test@test.com', None, None, 'I1C 8X3') is False
    assert update_user('update.Test@test.com', None, None, 'O1C 8X3') is False
    assert update_user('update.Test@test.com', None, None, 'Q1C 8X3') is False
    assert update_user('update.Test@test.com', None, None, 'U1C 8X3') is False
    assert update_user('update.Test@test.com', None, None, 'Z1C 8X3') is False


def test_r3_4_update_user():
    '''
    Testing R3-4: User name has to be non-empty, alphanumeric-only,
    and space allowed only if it is not as the prefix or suffix.
    User name also has to be longer than 2 characters and less
    than 20 characters.
    '''

    assert update_user('update.Test@test.com', 'ValidName') is True
    assert update_user('update.Test@test.com', '',) is False
    assert update_user('update.Test@test.com', 'user@}') is False
    assert update_user('update.Test@test.com', ' user',) is False
    assert update_user('update.Test@test.com', 'user ',) is False
    assert update_user('update.Test@test.com', 'us er',) is True
    assert update_user('update.Test@test.com', '2c') is True
    assert update_user('update.Test@test.com',
                       'exactly20characterss') is True
    assert update_user('update.Test@test.com',
                       'within2and20char') is True
    assert update_user('update.Test@test.com',
                       'longerthan20characters') is False
    assert update_user('update.Test@test.com',
                       '1') is False

# Used to clear the db table after each test


def clearTable():
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        db.session.execute(table.delete())
    db.session.commit()

# Products can not have the same name


def test_r4_8_create_product():
    register('iPhoneMan', 'iPhoneMan@phone.com', '@Password')
    create_product(1000, "Burrito", "This is a very very expensive Burrito",
                   "2021-02-17", "iPhoneMan@phone.com")
    assert create_product(1000, "iPhone",
                          "This is a very very expensive phone",
                          "2021-02-17", "iPhoneMan@phone.com") is True
    assert create_product(1000, "Burrito",
                          "This is a very very expensive Burrito",
                          "2021-02-17", "iPhoneMan@phone.com") is False
    clearTable()

# Product names must be alphanuermic-only, and spaces allowed only if
# it is not as a prefix and suffix


def test_r4_1_create_product():
    register('iPhoneMan', 'iPhoneMan@phone.com', '@Password')
    assert create_product(1000, "iPhone",
                          "This is a very very expensive phone",
                          "2021-02-17", "iPhoneMan@phone.com") is True
    assert create_product(1000, " iPhone",
                          "This is a very very expensive phone",
                          "2021-02-17", "iPhoneMan@phone.com") is False
    assert create_product(1000, "iPhone ",
                          "This is a very very expensive phone",
                          "2021-02-17", "iPhoneMan@phone.com") is False
    assert create_product(1000, "iPhone$$$$",
                          "This is a very very expensive phone",
                          "2021-02-17", "iPhoneMan@phone.com") is False
    clearTable()

# Product names can not be too long


def test_r4_2_create_product():
    register('iPhoneMan', 'iPhoneMan@phone.com', '@Password')
    assert create_product(1000, "iPhone",
                          "This is a very very expensive phone",
                          "2021-02-17", "iPhoneMan@phone.com") is True
    assert create_product(1000, """kahdlkahdlkahdlkhakdhajdkshaldhadhahdlahdah
    kdhadkljahdkljashdkahdhasdhakhdklsahkdahhdlahldasdasdskadkjalhdkjlashdklja
    hdklashkdslahkadhkahdlkjahjd""",
                          """kahdlkahdlkahdlkhakdhajdkshaldhadhahdlahdahkdhadk
                          ljahdkljashdkahdhasdhakhdklsahkdahhdlahldasdasdskadk
                          jalhdkjlashdkljahdklashkdslahkadhkahdlkjahjd
    This is a very very expensive phone""", "2021-02-17",
                          "iPhoneMan@phone.com") is False

    clearTable()

# Product descriptions can not be too long


def test_r4_3_create_product():
    register('iPhoneMan', 'iPhoneMan@phone.com', '@Password')
    assert create_product(1000, "iPhone",
                          "This is a very very expensive phone",
                          "2021-02-17", "iPhoneMan@phone.com") is True
    assert create_product(1000, "iPhoneTwo", "expensive phone",
                          "2021-02-17", "iPhoneMan@phone.com") is False
    assert create_product(1000, "iPhoneThree", """dkjalhdkljahdkljashdkahdjsha
                         daljhdklsahdashdkahdahdalhkdajkndkjasldhaiyuodgwhadha
                         iodnbkadwkjlsandklanxcjkahsdkahdwiuahdksdladjkadhaakd
                         dkjalhdkljahdkljashdkahdjshadaljhdklsahdashdkahdahdal
                         hkdajkndkjasldhaiyuodgwhadhaiodnbkadwkjlsandklanxcjka
                         hsdkahdwiuahdksdladjkadhaakddkjalhdkljahdkljashdkahdj
                         shadaljhdklsahdashdkahdahdalhkdajkndkjasldhaiyuodgwha
                         dhaiodnbkadwkjlsandklanxcjkahsdkahdwiuahdksdladjkadha
                         akddkjalhdkljahdkljashdkahdjshadaljhdklsahdashdkahdah
                         dalhkdajkndkjasldhaiyuodgwhadhaiodnbkadwkjlsandklanxc
                         jkahsdkahdwiuahdksdladjkadhaakddkjalhdkljahdkljashdka
                         hdjshadaljhdklsahdashdkahdahdalhkdajkndkjasldhaiyuodg
                         whadhaiodnbkadwkjlsandklanxcjkahsdkahdwiuahdksdladjka
                         dhaakddkjalhdkljahdkljashdkahdjshadaljhdklsahdashdkah
                         dahdalhkdajkndkjasldhaiyuodgwhadhaiodnbkadwkjlsandkla
                         nxcjkahsdkahdwiuahdksdladjkadhaakddkjalhdkljahdkljash
                         dkahdjshadaljhdklsahdashdkahdahdalhkdajkndkjasldhaiyu
                         odgwhadhaiodnbkadwkjlsandklanxcjkahsdkahdwiuahdksdlad
                         jkadhaakddkjalhdkljahdkljashdkahdjshadaljhdklsahdashd
                         kahdahdalhkdajkndkjasldhaiyuodgwhadhaiodnbkadwkjlsand
                         klanxcjkahsdkahdwiuahdksdladjkadhaakddkjalhdkljahdklj
                         ashdkahdjshadaljhdklsahdashdkahdahdalhkdajkndkjasldha
                         iyuodgwhadhaiodnbkadwkjlsandklanxcjkahsdkahdwiuahdksd
                         ladjkadhaakddkjalhdkljahdkljashdkahdjshadaljhdklsahda
                         shdkahdahdalhkdajkndkjasldhaiyuodgwhadhaiodnbkadwkjls
                         andklanxcjkahsdkahdwiuahdksdladjkadhaakddkjalhdkljahd
                         kljashdkahdjshadaljhdklsahdashdkahdahdalhkdajkndkjasl
                         dhaiyuodgwhadhaiodnbkadwkjlsandklanxcjkahsdkahdwiuahd
                         ksdladjkadhaakddkjalhdkljahdkljashdkahdjshadaljhdklsa
                         hdashdkahdahdalhkdajkndkjasldhaiyuodgwhadhaiodnbkadwk
                         jlsandklanxcjkahsdkahdwiuahdksdladjkadhaakddkjalhdklj
                         ahdkljashdkahdjshadaljhdklsahdashdkahdahdalhkdajkndkj
                         asldhaiyuodgwhadhaiodnbkadwkjlsandklanxcjkahsdkahdwiu
                         ahdksdladjkadhaakddkjalhdkljahdkljashdkahdjshadaljhdk
                         lsahdashdkahdahdalhkdajkndkjasldhaiyuodgwhadhaiodnbka
                         dwkjlsandklanxcjkahsdkahdwiuahdksdladjkadhaakddkjalhd
                         kljahdkljashdkahdjshadaljhdklsahdashdkahdahdalhkdajkn
                         dkjasldhaiyuodgwhadhaiodnbkadwkjlsandklanxcjkahsdkahd
                         wiuahdksdladjkadhaakddkjalhdkljahdkljashdkahdjshadalj
                         hdklsahdashdkahdahdalhkdajkndkjasldhaiyuodgwhadhaiodn
                         bkadwkjlsandklanxcjkahsdkahdwiuahdksdladjkadhaakddkja
                         lhdkljahdkljashdkahdjshadaljhdklsahdashdkahdahdalhkda
                         jkndkjasldhaiyuodgwhadhaiodnbkadwkjlsandklanxcjkahsdk
                         ahdwiuahdksdladjkadhaakddkjalhdkljahdkljashdkahdjshad
                         aljhdklsahdashdkahdahdalhkdajkndkjasldhaiyuodgwhadhai
                         odnbkadwkjlsandklanxcjkahsdkahdwiuahdksdladjkadhaakdd
                         kjalhdkljahdkljashdkahdjshadaljhdklsahdashdkahdahdalh
                         kdajkndkjasldhaiyuodgwhadhaiodnbkadwkjlsandklanxcjkah
                         sdkahdwiuahdksdladjkadhaakddkjalhdkljahdkljashdkahdjs
                         hadaljhdklsahdashdkahdahdalhkdajkndkjasldhaiyuodgwhad
                         haiodnbkadwkjlsandklanxcjkahsdkahdwiuahdksdladjkadhaa
                         kddkjalhdkljahdkljashdkahdjshadaljhdklsahdashdkahdahd
                         alhkdajkndkjasldhaiyuodgwhadhaiodnbkadwkjlsandklanxcj
                         kahsdkahdwiuahdksdladjkadhaakddkjalhdkljahdkljashdkah
                         djshadaljhdklsahdashdkahdahdalhkdajkndkjasldhaiyuodgw
                         hadhaiodnbkadwkjlsandklanxcjkahsdkahdwiuahdksdladjkad
                         haakddkjalhdkljahdkljashdkahdjshadaljhdklsahdashdkahd
                         ahdalhkdajkndkjasldhaiyuodgwhadhaiodnbkadwkjlsandklan
                         xcjkahsdkahdwiuahdksdladjkadhaakddkjalhdkljahdkljashd
                         kahdjshadaljhdklsahdashdkahdahdalhkdajkndkjasldhaiyuo
                         dgwhadhaiodnbkadwkjlsandklanxcjkahsdkahdwiuahdksdladj
                         kadhaakd""",
                          "2021-02-17", "iPhoneMan@phone.com") is False

    clearTable()

# Product description has to be longer than title


def test_r4_4_create_product():
    register('iPhoneMan', 'iPhoneMan@phone.com', '@Password')
    assert create_product(1000, "iPhone",
                          "This is a very very expensive phone",
                          "2021-02-17", "iPhoneMan@phone.com") is True
    assert create_product(1000, "iPhoneTwo", ".d",
                          "2021-02-17", "iPhoneMan@phone.com") is False

    clearTable()

# Product price has to be in a certain range [10 - 10000]


def test_r4_5_create_product():
    register('iPhoneMan', 'iPhoneMan@phone.com', '@Password')
    assert create_product(1000, "iPhone",
                          "This is a very very expensive phone",
                          "2021-02-17", "iPhoneMan@phone.com") is True
    assert create_product(9, "iPhoneTwo",
                          "This is a very very expensive phone",
                          "2021-02-17", "iPhoneMan@phone.com") is False
    assert create_product(10001, "iPhoneThree",
                          "This is a very very expensive phone",
                          "2021-02-17", "iPhoneMan@phone.com") is False

    clearTable()

# Product date has to be in a certain range (2021-01-02 - 2025-01-02)


def test_r4_6_create_product():
    register('iPhoneMan', 'iPhoneMan@phone.com', '@Password')
    assert create_product(1000, "iPhone",
                          "This is a very very expensive phone",
                          "2021-02-17", "iPhoneMan@phone.com") is True
    assert create_product(1000, "iPhoneTwo",
                          "This is a very very expensive phone",
                          "2019-02-17", "iPhoneMan@phone.com") is False
    assert create_product(1000, "iPhoneThree",
                          "This is a very very expensive phone",
                          "2021-01-01", "iPhoneMan@phone.com") is False
    assert create_product(1000, "iPhoneFour",
                          "This is a very very expensive phone",
                          "2026-01-01", "iPhoneMan@phone.com") is False
    assert create_product(1000, "iPhoneFive",
                          "This is a very very expensive phone",
                          "2025-02-01", "iPhoneMan@phone.com") is False
    assert create_product(1000, "iPhoneSix",
                          "This is a very very expensive phone",
                          "2025-01-02", "iPhoneMan@phone.com") is False

    clearTable()
# Owner email can not be empty and unique


def test_r4_7_create_product():
    register('iPhoneMan', 'iPhoneMan@phone.com', '@Password')
    assert create_product(1000, "iPhone",
                          "This is a very very expensive phone",
                          "2021-02-17", "iPhoneMan@phone.com") is True
    assert create_product(1000, "iPhoneTwo",
                          "This is a very very expensive phone",
                          "2021-02-17", "") is False
    assert create_product(1000, "iPhoneThree",
                          "This is a very very expensive phone",
                          "2021-02-17", "Bobby") is False

    clearTable()


def test_r5_1_update_product():
    '''
    Testing R5-1: One can update all attributes of the product,
    except owner_email and last_modified_date.
    '''
    register("CoolGuy", "iPhoneMan@phone.com", "@CoolPassword")
    create_product(1000, "iPhone", "This is a very very expensive phone",
                   "2021-02-17", "iPhoneMan@phone.com")
    assert update_product(
        1000, "iPhoneTwo",
        "This is a very very expensive phone", "iPhone") is True
    assert update_product(
        1000, "iPhoneThree",
        "This is a very very expensive phone", "gjf") is False

    clearTable()


def test_r5_2_update_product():
    '''
    R5-2: Price can be only increased but cannot be decreased
    '''
    register("CoolGuy", "iPhoneMan@phone.com", "@CoolPassword")
    create_product(1000, "iPhone", "This is a very very expensive phone",
                   "2021-02-17", "iPhoneMan@phone.com")
    assert update_product(
        1100, "iPhoneTwo",
        "This is a very very expensive phone", "iPhone") is True
    assert update_product(
        900, "iPhoneThree",
        "This is a very very expensive phone", "iPhone") is False

    clearTable()


def test_r5_4_update_product():
    '''
    R5-4: When updating an attribute,
    one has to make sure that it follows the same requirements as above.
    '''
    register("CoolGuy", "iPhoneMan@phone.com", "@CoolPassword")
    create_product(1000, "iPhone", "This is a very very expensive phone",
                   "2021-02-17", "iPhoneMan@phone.com")
    assert update_product(
        1100, "iPhoneTwo",
        "This is a very very expensive phone", "iPhone") is True
    assert update_product(
        1000, "iPhoneThree",
        "This is a very very expensive phone", "gjf") is False
    assert update_product(
        900, "iPhoneThree",
        "This is a very very expensive phone", "iPhoneTwo") is False


def test_r5_3_update_product():
    '''
    R5-3: last_modified_date should be updated when the
    update operation is successful.
    '''
    register("CoolGuy", "iPhoneMan@phone.com", "@CoolPassword")
    create_product(1000, "iPhone", "This is a very very expensive phone",
                   "2021-02-17", "iPhoneMan@phone.com")
    assert update_product(
        1100, "iPhoneTwo",
        "This is a very very expensive phone", "iPhone") is True


def test_transactions():
    """
    test_transactions tries completing purchase orders iff
    the purchaser is not already the product owner, and the product
    is not worth more than the buyer's account balance
    """

    register("Transtest", "Transaction@test.email", "@Password")
    
    register("Actiontest", "Transaction1@test.email", "@Password")
    
    # This product's value is higher than Transtest balance, should fail.
    create_product(1000, "expensive", "This product is worth more than 500",
                   "2021-12-03", "Transaction1@test.email")

    assert place_order("Transaction@test.email", "expensive") is False
    
    # This product was listed by the same user trying to buy it, should fail.
    create_product(100, "My product", "This product is worth less than 500",
                   "2021-12-03", "Transaction@test.email")
    
    assert place_order("Transaction@test.email", "My product") is False
    
    # This is a valid product to purchase, should pass.
    create_product(100, "affordable", "This product is worth less than 500",
                   "2021-12-03", "Transaction1@test.email")
    
    assert place_order("Transaction@test.email", "affordable") is True