import smartpy as sp
# Both buyer and seller must send in twice the value of the item they are transacting on. This ensures that both parties are committed to see the transaction through to the end.
# Original implementation can be found https://medium.com/@solled/an-escrow-smart-contract-in-smartpy-4ca80a0a28c6
# But the original one cannot run on latest SmartPy IDE already, so i made some change to make it can run.
class Escrow(sp.Contract):
    def __init__(self):
        self.init(seller = sp.none, buyer = sp.none, price = 0)
        
    @sp.entry_point
    def setSeller(self, params):
        #ensure seller hasn't already been set
        sp.verify (~self.data.seller.is_some())
        
        #the seller sets the price and must send 2x the price in tez
        self.data.price = params.price
        sp.verify (sp.amount == sp.tez(self.data.price * 2))
        self.data.seller = sp.some(sp.sender)
        
    @sp.entry_point
    def setBuyer(self, params):
        #ensure that there already is a seller
        sp.verify (self.data.seller.is_some())
        #ensure buyer hasnt already been set
        sp.verify (~self.data.buyer.is_some())
        
        sp.verify (sp.amount == sp.tez(self.data.price * 2))
        self.data.buyer = sp.some(sp.sender)
        
    @sp.entry_point
    def confirmReceived(self, params):
        sp.verify (sp.sender == self.data.buyer.open_some())
        sp.send (self.data.buyer.open_some(), sp.tez(self.data.price))
        sp.send (self.data.seller.open_some(), sp.balance)
        self.resetContract()
        
    @sp.entry_point
    def refundBuyer(self, params):
        sp.verify (sp.sender == self.data.seller.open_some())
        sp.send (self.data.buyer.open_some(), sp.tez(2 * self.data.price))
        sp.send (self.data.seller.open_some(), sp.balance)
        self.resetContract()
        
    #clear out buyer and seller
    def resetContract(self):
        self.data.buyer = sp.none
        self.data.seller = sp.none
        self.data.price = 0
        
    @sp.add_test(name = "Test Escrow")
    def testEscrow():
        scenario = sp.test_scenario()
        seller = "tz2AAA"
        buyer = "tz2BBB"
        myContract = Escrow()
        #set the seller and price
        scenario += myContract
        scenario += myContract.setSeller(price = 1).run(sp.address(seller), amount = sp.tez(2))
      
        #set the buyer
        scenario += myContract.setBuyer().run(sp.address(buyer), amount = sp.tez(2))
      
        # buyer confirms they received item 
        scenario += myContract.confirmReceived().run(sp.address("tz2BBB"))
      
