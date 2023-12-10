from django.db import models


class Driver(models.Model): 
    license_number = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Truck(models.Model):
    
    driver = models.OneToOneField(Driver, on_delete=models.CASCADE)
    license_plate = models.CharField(max_length=11, unique=True)    
    capacity = models.IntegerField()
    
    def __str__(self):
        return f"{self.license_plate}"


class CargoOrder(models.Model):
    NOT_STARTED = 'not started'
    IN_PROGRESS = 'in progress'
    COMPLETED = 'completed'
    IN_QUEUE = 'in queue'

    STATUS_CHOICES = [
        (NOT_STARTED, 'Not Started'),
        (IN_PROGRESS, 'In Progress'),
        (COMPLETED, 'Completed'),
        (IN_QUEUE, 'In Queue'),
    ]
    truck = models.ForeignKey(Truck, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=NOT_STARTED
    )
    DESTINATION_CHOICES = [
        ("Aghdam", "Aghdam"),
        ("Agdash", "Agdash"),
        ("Aghjabadi", "Aghjabadi"),
        ("Agstafa", "Agstafa"),
        ("Agsu", "Agsu"),
        ("Astara", "Astara"),
        ("Aghdara", "Aghdara"),
        ("Babek", "Babek"),
        ("Baku", "Baku"),
        ("Balakən", "Balakən"), 
        ("Barda", "Barda"),
        ("Beylagan", "Beylagan"),
        ("Bilasuvar", "Bilasuvar"),
        ("Dashkasan", "Dashkasan"),
        ("Shabran", "Shabran"),
        ("Fuzuli", "Fuzuli"),
        ("Gadabay", "Gadabay"),
        ("Ganja", "Ganja"),
        ("Goranboy", "Goranboy"),
        ("Goychay", "Goychay"),
        ("Goygol", "Goygol"),
        ("Hajigabul", "Hajigabul"),
        ("Imishli", "Imishli"),
        ("Ismayilli", "Ismayilli"),
        ("Jabrayil", "Jabrayil"),
        ("Julfa", "Julfa"),
        ("Kalbajar", "Kalbajar"),
        ("Khachmaz", "Khachmaz"),
        ("Khankendi", "Khankendi"),
        ("Khojavend", "Khojavend"),
        ("Khirdalan", "Khirdalan"),
        ("Kurdamir", "Kurdamir"),
        ("Lankaran", "Lankaran"),
        ("Lerik", "Lerik"),
        ("Masally", "Masally"),
        ("Mingachevir", "Mingachevir"),
        ("Nakhchivan", "Nakhchivan"),
        ("Naftalan", "Naftalan"),
        ("Neftchala", "Neftchala"),
        ("Oghuz", "Oghuz"),
        ("Ordubad", "Ordubad"),
        ("Qabala", "Qabala"),
        ("Qakh", "Qakh"),
        ("Qazakh", "Qazakh"),
        ("Quba", "Quba"),
        ("Qubadli", "Qubadli"),
        ("Qusar", "Qusar"),
        ("Saatlı", "Saatlı"),
        ("Sabirabad", "Sabirabad"),
        ("Shahbuz", "Shahbuz"),
        ("Shaki", "Shaki"),
        ("Shamakhi", "Shamakhi"),
        ("Shamkir", "Shamkir"),
        ("Sharur", "Sharur"),
        ("Shirvan", "Shirvan"),
        ("Siyazan", "Siyazan"),
        ("Shusha", "Shusha"),
        ("Sumgait", "Sumgait"),
        ("Tartar", "Tartar"),
        ("Tovuz", "Tovuz"),
        ("Ujar", "Ujar"),
        ("Yardimli", "Yardimli"),
        ("Yevlakh", "Yevlakh"),
        ("Zaqatala", "Zaqatala"),
        ("Zardab", "Zardab"),
        ("Zangilan", "Zangilan")
    ]
    
    load = models.IntegerField(default=10);
        
    start_point = models.CharField(
        max_length=50,
        choices=DESTINATION_CHOICES,
        default="Baku"
    )
        
    destination = models.CharField(
        max_length=50,
        choices=DESTINATION_CHOICES,
        default="Sumgayit"
    )
    
    def __str__(self):
        return f"{self.start_point}-{self.destination}"
    
    